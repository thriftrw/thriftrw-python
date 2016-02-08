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

from libc.stdint cimport (
    int8_t,
    int16_t,
    int32_t,
    int64_t,
)


cdef class ValueVisitor(object):

    cdef object visit_bool(self, bint value)

    cdef object visit_byte(self, int8_t value)

    cdef object visit_double(self, double value)

    cdef object visit_i16(self, int16_t value)

    cdef object visit_i32(self, int32_t value)

    cdef object visit_i64(self, int64_t value)

    cdef object visit_binary(self, bytes value)

    cdef object visit_struct(self, list fields)

    cdef object visit_map(self, int8_t key_ttype, int8_t value_ttype, list pairs)

    cdef object visit_set(self, int8_t value_ttype, list values)

    cdef object visit_list(self, int8_t value_ttype, list values)


cdef class _ValueVisitorArgs(ValueVisitor):
    pass


cdef class Value(object):

    cpdef object apply(Value self, ValueVisitor visitor)


cdef class BoolValue(Value):
    cdef readonly bint value


cdef class ByteValue(Value):
    cdef readonly int8_t value


cdef class DoubleValue(Value):
    cdef readonly double value


cdef class I16Value(Value):
    cdef readonly int16_t value


cdef class I32Value(Value):
    cdef readonly int32_t value


cdef class I64Value(Value):
    cdef readonly int64_t value


cdef class BinaryValue(Value):
    cdef readonly bytes value
    # TODO change to char* once BinaryProtocol knows how to write that.


cdef class FieldValue(object):
    cdef readonly int16_t id
    cdef readonly int8_t ttype
    cdef readonly object value


cdef class StructValue(Value):
    cdef readonly list fields
    cdef readonly dict _index


cdef class MapItem(object):
    cdef readonly object key
    cdef readonly object value


cdef class MapValue(Value):
    cdef readonly int8_t key_ttype
    cdef readonly int8_t value_ttype
    cdef readonly list pairs


cdef class SetValue(Value):
    cdef readonly int8_t value_ttype
    cdef readonly list values


cdef class ListValue(Value):
    cdef readonly int8_t value_ttype
    cdef readonly list values
