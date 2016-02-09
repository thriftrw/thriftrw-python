# Copyright (c) 2015 Uber Technologies, Inc.
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

from thriftrw.wire cimport ttype
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
    """TypeSpec for primitive types."""

    def __init__(self, name, code, value_cls, surface, cast=None):
        """
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
        """
        self.name = unicode(name)
        self.code = code
        self.value_cls = value_cls
        self.surface = surface

        if cast is None:
            cast = (lambda x: x)
        self.cast = cast

    @property
    def ttype_code(self):
        return self.code

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
        # TODO check bounds for numeric values
        check.instanceof_surface(self, instance)

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

    ttype_code = ttype.BINARY

    cpdef TypeSpec link(self, scope):
        return self

    cpdef Value to_wire(_TextualTypeSpec self, object value):
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        return BinaryValue(value)

    cpdef void validate(_TextualTypeSpec self, object instance) except *:
        if not isinstance(instance, (bytes, unicode)):
            raise TypeError(
                'Cannot convert %r into a "%s".' % (instance, self.name)
            )


cdef class _TextTypeSpec(_TextualTypeSpec):
    """TypeSpec for the text type."""

    name = 'string'
    surface = unicode

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

    name = 'binary'
    surface = bytes

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

    name = 'bool'
    surface = bool
    ttype_code = ttype.BOOL

    cpdef Value to_wire(_BoolTypeSpec self, object value):
        return BoolValue(bool(value))

    cpdef object to_primitive(_BoolTypeSpec self, object value):
        return bool(value)

    cpdef object from_wire(_BoolTypeSpec self, Value wire_value):
        check.type_code_matches(self, wire_value)
        return wire_value.value

    cpdef object from_primitive(_BoolTypeSpec self, object prim_value):
        return bool(prim_value)

    cpdef TypeSpec link(self, scope):
        return self

    cpdef void validate(_BoolTypeSpec self, object instance) except *:
        check.instanceof_class(self, (bool, int), instance)

    def __richcmp__(_BoolTypeSpec self, _BoolTypeSpec other, int op):
        if op == 2:
            return self is other
        else:
            return False


BoolTypeSpec = _BoolTypeSpec()

ByteTypeSpec = PrimitiveTypeSpec(
    'byte', ttype.BYTE, ByteValue, (int, long), int
)

DoubleTypeSpec = PrimitiveTypeSpec(
    'double', ttype.DOUBLE, DoubleValue, (int, long, float), float
)

I16TypeSpec = PrimitiveTypeSpec(
    'i16', ttype.I16, I16Value, (int, long), int
)

I32TypeSpec = PrimitiveTypeSpec(
    'i32', ttype.I32, I32Value, (int, long), int
)

I64TypeSpec = PrimitiveTypeSpec(
    'i64', ttype.I64, I64Value, (int, long), long
)

BinaryTypeSpec = _BinaryTypeSpec()

TextTypeSpec = _TextTypeSpec()
