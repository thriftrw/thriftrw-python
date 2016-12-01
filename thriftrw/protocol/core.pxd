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

from thriftrw.wire cimport ttype
from thriftrw.wire.value cimport Value, ValueVisitor
from thriftrw.wire.message cimport Message
from thriftrw._buffer cimport WriteBuffer, ReadBuffer


cdef struct FieldHeader:
    int8_t type
    int16_t id


cdef class MapHeader(object):
    cdef readonly int8_t ktype
    cdef readonly int8_t vtype
    cdef readonly int32_t size


cdef class SetHeader(object):
    cdef readonly int8_t type
    cdef readonly int32_t size


cdef class ListHeader(object):
    cdef readonly int8_t type
    cdef readonly int32_t size


cdef class MessageHeader(object):
    cdef readonly bytes name
    cdef readonly int8_t type
    cdef readonly int32_t seqid


cdef class ProtocolWriter(object):

    cdef void write_value(self, Value value) except *

    # Primitives

    cdef void write_bool(self, bint value) except *
    cdef void write_byte(self, int8_t value) except *
    cdef void write_double(self, double value) except *
    cdef void write_i16(self, int16_t value) except *
    cdef void write_i32(self, int32_t value) except *
    cdef void write_i64(self, int64_t value) except *
    cdef void write_binary(self, char* value, int32_t length) except *

    # Structs

    cdef void write_struct_begin(self) except *
    cdef void write_field_begin(self, FieldHeader header) except *
    cdef void write_field_end(self) except *
    cdef void write_struct_end(self) except *

    # Containers

    cdef void write_map_begin(self, MapHeader header) except *
    cdef void write_map_end(self) except *

    cdef void write_set_begin(self, SetHeader header) except *
    cdef void write_set_end(self) except *

    cdef void write_list_begin(self, ListHeader header) except *
    cdef void write_list_end(self) except *

    # Messages

    cdef void write_message_begin(self, MessageHeader header) except *
    cdef void write_message_end(self) except *


cdef class ProtocolReader:

    # Skip

    cdef void skip(self, int typ) except *
    cdef void skip_binary(self) except *
    cdef void skip_map(self) except *
    cdef void skip_list(self) except *
    cdef void skip_set(self) except *
    cdef void skip_struct(self) except *

    # Primitives

    cdef bint read_bool(self) except *
    cdef int8_t read_byte(self) except *
    cdef double read_double(self) except *
    cdef int16_t read_i16(self) except *
    cdef int32_t read_i32(self) except *
    cdef int64_t read_i64(self) except *
    cdef bytes read_binary(self)

    # Structs

    cdef void read_struct_begin(self) except *
    cdef FieldHeader read_field_begin(self)
    cdef void read_field_end(self) except *
    cdef void read_struct_end(self) except *

    # Containers

    cdef MapHeader read_map_begin(self)
    cdef void read_map_end(self) except *

    cdef SetHeader read_set_begin(self)
    cdef void read_set_end(self) except *

    cdef ListHeader read_list_begin(self)
    cdef void read_list_end(self) except *

    # Messages

    cdef MessageHeader read_message_begin(self)
    cdef void read_message_end(self) except *


cdef class Protocol(object):
    cpdef ProtocolWriter writer(self, WriteBuffer buff)

    cpdef ProtocolReader reader(self, ReadBuffer buff)

    cpdef bytes serialize_value(self, Value value)

    cpdef Value deserialize_value(self, int typ, bytes s)

    cpdef bytes serialize_message(self, Message message)

    cpdef Message deserialize_message(self, bytes s)


cdef class _ValueWriter(ValueVisitor):
    cdef ProtocolWriter writer
