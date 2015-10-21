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

from libc.stdlib cimport malloc, realloc, free
from libc.string cimport memcpy


cdef int DEFAULT_CAPACITY = 4096  # 4k


cdef class WriteBuffer(object):
    """A write-only in-memory buffer.

    It defaults to a 4k sized buffer.

    The ``value`` attribute makes all data written to the buffer so far
    available as a Python ``bytes`` object.
    """

    def __cinit__(self, int init_capacity=0):
        """
        :param int init_capacity:
            Initial capacity of the write buffer.
        """
        init_capacity = init_capacity or DEFAULT_CAPACITY

        self.data = <char*>malloc(init_capacity)
        self.length = 0
        self.capacity = init_capacity

    def __dealloc__(self):
        if self.data != NULL:
            free(self.data)
            self.data = NULL

    cpdef void clear(self):
        """Clears the buffer."""

        capacity = self.length + self.capacity
        self.length = 0
        self.capacity = capacity

    cpdef void write_bytes(self, bytes data):
        """Writes the given Python bytes object to the buffer.

        :param bytes data:
            Data to write to the buffer.
        """
        self.write(data, len(data))

    cdef void write(self, char *data, int count):
        """Writes bytes from the given memory block to the buffer.

        :param int data:
            Pointer to source data block.
        :param int count:
            Number of bytes to write.
        """
        self.ensure_capacity(count)

        memcpy(self.data + self.length, data, count)
        self.length += count
        self.capacity -= count

    cdef void ensure_capacity(self, int min_bytes):
        """Ensures that the buffer has enough room for at least ``min_bytes``
        more bytes.
        """
        if min_bytes <= self.capacity:
            return

        new_total_length = self.length * 2
        if new_total_length - self.length < min_bytes:
            # If adding as much room as the current buffer size is not enough,
            # add just enough room on top.
            new_total_length += min_bytes

        self.data = <char*>realloc(self.data, new_total_length)
        self.capacity = new_total_length - self.length

    property value:
        """Data written to the buffer so far."""

        def __get__(self):
            cdef bytes out = self.data[:self.length]
            return out
