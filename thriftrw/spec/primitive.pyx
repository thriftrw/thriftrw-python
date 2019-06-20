# Copyright (c) 2016 Uber Technologies, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import absolute_import, unicode_literals, print_function

import numbers
import decimal
import fractions

from thriftrw.wire cimport ttype
from thriftrw.protocol.core cimport ProtocolWriter, ProtocolReader
from thriftrw.wire.value cimport (
    Value,
    BoolValue,
    ByteValue,
    DoubleValue,
    I16Value,
    I32Value,
    I64Value,
    BinaryValue,
)

from . cimport check
from .base cimport TypeSpec

__all__ = [
    'BoolTypeSpec',
    'ByteTypeSpec',
    'DoubleTypeSpec',
    'I16TypeSpec',
    'I32TypeSpec',
    'I64TypeSpec',
    'BinaryTypeSpec',
    'TextTypeSpec',
]


cdef class PrimitiveTypeSpec(TypeSpec):
    """TypeSpec for primitive types.

    :param name:
        Name of the primitive type
    :param code:
        TType code used by this primitive
    :param value_cls:
        Constructor for wire value types
    :param surface:
        Values passed through this spec must be instances of this class or
        an exception will be raised
    :param cast:
        If provided, this is used to cast values into a standard shape
        before passing them to ``value_cls``
    :param validate_extra:
        If provided, this is used to validate values beyond checking that
        they have the correct type.
    """

    cpdef Value to_wire(self, object value):
        return self.value_cls(self.cast(value))

    cpdef object to_primitive(PrimitiveTypeSpec self, object value):
        return value

    cpdef object from_wire(PrimitiveTypeSpec self, Value wire_value):
        check.type_code_matches(self, wire_value)
        return wire_value.value

    cpdef object from_primitive(PrimitiveTypeSpec self, object prim_value):
        return self.cast(prim_value)

    cpdef TypeSpec link(self, scope):
        return self

    cpdef void validate(PrimitiveTypeSpec self, object instance) except *:
        check.instanceof_surface(self, instance)
        if self.validate_extra is not None:
            self.validate_extra(instance)

    def __str__(self):
        return 'PrimitiveTypeSpec(%r, %s)' % (self.code, self.value_cls)

    def __repr__(self):
        return str(self)

    def __richcmp__(PrimitiveTypeSpec self, PrimitiveTypeSpec other, int op):
        if op == 2:
            return self is other
        else:
            return False


cdef class _TextualTypeSpec(TypeSpec):

    def __init__(self):
        self.ttype_code = ttype.BINARY
        self.hashable = True

    cpdef TypeSpec link(self, scope):
        return self

    cpdef Value to_wire(_TextualTypeSpec self, object value):
        if type(value) is unicode:
            value = value.encode('utf-8')
        return BinaryValue(value)

    cpdef void write_to(_TextualTypeSpec self, ProtocolWriter writer,
                        object value) except *:
        if type(value) is unicode:
            value = value.encode('utf-8')
        writer.write_binary(value, len(value))

    cpdef void validate(_TextualTypeSpec self, object instance) except *:
        if not isinstance(instance, (bytes, unicode)):
            raise TypeError(
                'Cannot convert %r into a "%s".' % (instance, self.name)
            )


cdef class _TextTypeSpec(_TextualTypeSpec):
    """TypeSpec for the text type."""

    name = str('string')
    surface = unicode

    cpdef object read_from(_TextTypeSpec self, ProtocolReader reader):
        # TODO: Is this right?
        return reader.read_binary().decode('utf-8')

    cpdef object to_primitive(_TextTypeSpec self, object value):
        if isinstance(value, bytes):
            value = value.decode('utf-8')
        return value

    cpdef object from_wire(_TextTypeSpec self, Value wire_value):
        check.type_code_matches(self, wire_value)
        return wire_value.value.decode('utf-8')

    cpdef object from_primitive(_TextTypeSpec self, object prim_value):
        if isinstance(prim_value, bytes):
            prim_value = prim_value.decode('utf-8')
        return prim_value

    def __richcmp__(_TextTypeSpec self, _TextTypeSpec other, int op):
        if op == 2:
            return self is other
        else:
            return False


cdef class _BinaryTypeSpec(_TextualTypeSpec):

    name = str('binary')
    surface = bytes

    cpdef object read_from(_BinaryTypeSpec self, ProtocolReader reader):
        return reader.read_binary()

    cpdef object to_primitive(_BinaryTypeSpec self, object value):
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        return value

    cpdef object from_wire(_BinaryTypeSpec self, Value wire_value):
        check.type_code_matches(self, wire_value)
        return wire_value.value

    cpdef object from_primitive(_BinaryTypeSpec self, object prim_value):
        if isinstance(prim_value, unicode):
            prim_value = prim_value.encode('utf-8')
        return prim_value

    def __richcmp__(_BinaryTypeSpec self, _BinaryTypeSpec other, int op):
        if op == 2:
            return self is other
        else:
            return False


cdef class _BoolTypeSpec(TypeSpec):

    name = str('bool')
    surface = bool

    def __init__(self):
        self.ttype_code = ttype.BOOL

    cpdef object read_from(_BoolTypeSpec self, ProtocolReader reader):
        return reader.read_bool()

    cpdef Value to_wire(_BoolTypeSpec self, object value):
        return BoolValue(bool(value))

    cpdef object to_primitive(_BoolTypeSpec self, object value):
        return bool(value)

    cpdef object from_wire(_BoolTypeSpec self, Value wire_value):
        check.type_code_matches(self, wire_value)
        return wire_value.value

    cpdef object from_primitive(_BoolTypeSpec self, object prim_value):
        return bool(prim_value)

    cpdef void write_to(_BoolTypeSpec self, ProtocolWriter writer,
                        object value) except *:
        writer.write_bool(value)

    cpdef TypeSpec link(self, scope):
        return self

    cpdef void validate(_BoolTypeSpec self, object instance) except *:
        check.instanceof_class(self, (bool, int), instance)

    def __richcmp__(_BoolTypeSpec self, _BoolTypeSpec other, int op):
        if op == 2:
            return self is other
        else:
            return False


def validate_signed_int(bits):
    max_magnitude = 1 << (bits - 1)
    min_value = -1 * max_magnitude
    max_value = max_magnitude - 1
    def _validate_signed_int(x):
        if x < min_value or x > max_value:
            raise ValueError('Value %d does not fit in an i%d' % (x, bits))
    return _validate_signed_int


# Although the Integral and Number classes already cover int, long, (and
# everything else in case Number), we list those out here explicitly because
# old versions of PyPy or PyPy3 don't play well with isinstance checks
# generated by Cython.
_INTEGRAL = (int, long, numbers.Integral)
_FLOATING = (int, long, float, decimal.Decimal, fractions.Fraction,
             numbers.Number)

BoolTypeSpec = _BoolTypeSpec()

cdef class _ByteTypeSpec(PrimitiveTypeSpec):

    def __init__(self):
        self.name = str('byte')
        self.ttype_code = ttype.BYTE
        self.value_cls = ByteValue
        self.surface = _INTEGRAL
        self.cast = int
        self.validate_extra = validate_signed_int(8)

    cpdef void write_to(_ByteTypeSpec self, ProtocolWriter writer,
                        object value) except *:
        writer.write_byte(value)

    cpdef object read_from(_ByteTypeSpec self, ProtocolReader reader):
        return reader.read_byte()

ByteTypeSpec = _ByteTypeSpec()

cdef class _DoubleTypeSpec(PrimitiveTypeSpec):

    def __init__(self):
        self.name = str('double')
        self.ttype_code = ttype.DOUBLE
        self.value_cls = DoubleValue
        self.surface = _FLOATING
        self.cast = float

    cpdef void write_to(_DoubleTypeSpec self, ProtocolWriter writer,
                        object value) except *:
        writer.write_double(value)

    cpdef object read_from(_DoubleTypeSpec self, ProtocolReader reader):
        return reader.read_double()

DoubleTypeSpec = _DoubleTypeSpec()

cdef class _I16TypeSpec(PrimitiveTypeSpec):

    def __init__(self):
        self.name = str('i16')
        self.ttype_code = ttype.I16
        self.value_cls = I16Value
        self.surface = _INTEGRAL
        self.cast = int
        self.validate_extra = validate_signed_int(16)

    cpdef void write_to(_I16TypeSpec self, ProtocolWriter writer,
                        object value) except *:
        writer.write_i16(value)

    cpdef object read_from(_I16TypeSpec self, ProtocolReader reader):
        return reader.read_i16()

I16TypeSpec = _I16TypeSpec()

cdef class _I32TypeSpec(PrimitiveTypeSpec):

    def __init__(self):
        self.name = str('i32')
        self.ttype_code = ttype.I32
        self.value_cls = I32Value
        self.surface = _INTEGRAL
        self.cast = int
        self.validate_extra = validate_signed_int(32)

    cpdef void write_to(_I32TypeSpec self, ProtocolWriter writer,
                        object value) except *:
        writer.write_i32(value)

    cpdef object read_from(_I32TypeSpec self, ProtocolReader reader):
        return reader.read_i32()

I32TypeSpec = _I32TypeSpec()

cdef class _I64TypeSpec(PrimitiveTypeSpec):

    def __init__(self):
        self.name = str("i64")
        self.ttype_code = ttype.I64
        self.value_cls = I64Value
        self.surface = _INTEGRAL
        self.cast = long
        self.validate_extra = validate_signed_int(64)

    cpdef void write_to(_I64TypeSpec self, ProtocolWriter writer,
                        object value) except *:
        writer.write_i64(value)

    cpdef object read_from(_I64TypeSpec self, ProtocolReader reader):
        return reader.read_i64()

I64TypeSpec = _I64TypeSpec()

BinaryTypeSpec = _BinaryTypeSpec()

TextTypeSpec = _TextTypeSpec()
