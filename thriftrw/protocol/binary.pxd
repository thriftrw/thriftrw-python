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

from libc.stdint cimport (
    int8_t,
    int16_t,
    int32_t,
    int64_t,
)

from .core cimport (
    Protocol,
    ProtocolWriter,
    ProtocolReader,
    FieldHeader,
    MapHeader,
    SetHeader,
    ListHeader,
    MessageHeader,
)
from thriftrw.wire.message cimport Message
from thriftrw._buffer cimport ReadBuffer, WriteBuffer
from thriftrw.wire.value cimport (
    ValueVisitor,
    Value,
    BoolValue,
    ByteValue,
    DoubleValue,
    I16Value,
    I32Value,
    I64Value,
    BinaryValue,
    FieldValue,
    StructValue,
    MapValue,
    MapItem,
    SetValue,
    ListValue,
)


cdef class BinaryProtocol(Protocol):
    pass

cdef class BinaryProtocolReader(ProtocolReader):
    cdef ReadBuffer reader

    cdef void _read(self, char* data, int count) except *
    cdef int8_t _byte(self) except *
    cdef int16_t _i16(self) except *
    cdef int32_t _i32(self) except *
    cdef int64_t _i64(self) except *
    cdef double _double(self) except *


cdef class BinaryProtocolWriter(ProtocolWriter):
    cdef WriteBuffer writer

    cdef void _write(BinaryProtocolWriter self, char* data, int length)


cdef class _OldBinaryProtocolReader(object):
    cdef ReadBuffer reader

    cdef object _reader(self, int8_t typ)

    cpdef object read(self, int8_t typ)

    cdef void _read(self, char* data, int count) except *

    cdef int8_t _byte(self) except *

    cdef int16_t _i16(self) except *

    cdef int32_t _i32(self) except *

    cdef int64_t _i64(self) except *

    cdef double _double(self) except *

    cdef Message read_message(self)

    cdef BoolValue read_bool(self)

    cdef ByteValue read_byte(self)

    cdef DoubleValue read_double(self)

    cdef I16Value read_i16(self)

    cdef I32Value read_i32(self)

    cdef I64Value read_i64(self)

    cdef BinaryValue read_binary(self)

    cdef StructValue read_struct(self)

    cdef MapValue read_map(self)

    cdef SetValue read_set(self)

    cdef ListValue read_list(self)
