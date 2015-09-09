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

import six

from thriftrw.wire import TType
from thriftrw.wire.value import (
    BoolValue,
    ByteValue,
    DoubleValue,
    I16Value,
    I32Value,
    I64Value,
    BinaryValue,
)

from . import check
from .base import TypeSpec

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


class PrimitiveTypeSpec(TypeSpec):
    """TypeSpec for primitive types."""

    __slots__ = ('name', 'code', 'value_cls', 'surface')

    def __init__(self, name, code, value_cls, surface):
        self.name = name
        self.code = code
        self.value_cls = value_cls
        self.surface = surface

    @property
    def ttype_code(self):
        return self.code

    def to_wire(self, value):
        check.instanceof_surface(self, value)
        # TODO check bounds for numeric values.
        return self.value_cls(value)

    def from_wire(self, wire_value):
        check.type_code_matches(self, wire_value)
        return wire_value.value

    def link(self, scope):
        return self

    def __str__(self):
        return 'PrimitiveType(%r, %s)' % (self.code, self.value_cls)

    __repr__ = __str__


class _TextTypeSpec(TypeSpec):
    """TypeSpec for the text type."""

    __slots__ = ()

    name = 'string'
    surface = six.text_type

    @property
    def ttype_code(self):
        return TType.BINARY

    def to_wire(self, value):
        if isinstance(value, six.text_type):
            value = value.encode('utf-8')
        elif not isinstance(value, six.binary_type):
            raise TypeError(
                'Cannot serialize %r into a "string".' % (value,)
            )
        return BinaryValue(value)

    def from_wire(self, wire_value):
        check.type_code_matches(self, wire_value)
        return wire_value.value.decode('utf-8')

    def link(self, scope):
        return self


#: TypeSpec for boolean values.
BoolTypeSpec = PrimitiveTypeSpec('bool', TType.BOOL, BoolValue, bool)

#: TypeSpec for single-byte integers.
ByteTypeSpec = PrimitiveTypeSpec('byte', TType.BYTE, ByteValue, int)

#: TypeSpec for floating point numbers with 64 bits of precision.
DoubleTypeSpec = PrimitiveTypeSpec('double', TType.DOUBLE, DoubleValue, float)

#: TypeSpec for 16-bit integers.
I16TypeSpec = PrimitiveTypeSpec('i16', TType.I16, I16Value, int)

#: TypeSpec for 32-bit integers.
I32TypeSpec = PrimitiveTypeSpec('i32', TType.I32, I32Value, int)

#: TypeSpec for 64-bit integers.
I64TypeSpec = PrimitiveTypeSpec('i64', TType.I64, I64Value, int)

#: TypeSpec for binary blobs.
BinaryTypeSpec = PrimitiveTypeSpec(
    'binary', TType.BINARY, BinaryValue, six.binary_type
)

#: TypeSpec for unicode data.
#:
#: Values will be decoded/encoded using UTF-8 encoding before/after being
#: serialized/deserialized.
#:
#: .. versionchanged:: 0.3.1
#:
#:     Allows passing binary values directly.
TextTypeSpec = _TextTypeSpec()
