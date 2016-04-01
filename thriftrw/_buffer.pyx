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

from io import BytesIO

from libc.string cimport memcpy

from .errors import EndOfInputError


cdef class WriteBuffer(object):
    """A write-only in-memory buffer.

    The ``value`` attribute makes all data written to the buffer so far
    available as a Python ``bytes`` object.
    """

    def __init__(self):
        self.buff = BytesIO()

    cpdef void clear(self):
        """Clears the buffer."""
        self.buff = BytesIO()

    cpdef void write_bytes(self, bytes data):
        """Writes the given Python bytes object to the buffer.

        :param bytes data:
            Data to write to the buffer.
        """
        self.buff.write(data)

    cdef void write(self, char* data, int count):
        """Writes bytes from the given memory block to the buffer.

        :param int data:
            Pointer to source data block.
        :param int count:
            Number of bytes to write.
        """
        self.buff.write(data[:count])

    property value:
        """Data written to the buffer so far."""

        def __get__(self):
            return self.buff.getvalue()


cdef class ReadBuffer(object):
    """A read-only in-memory buffer."""

    def __cinit__(self, bytes data):
        """Initialize a ReadBuffer that reads from the given ``bytes``.

        :param bytes data:
            Block of data that this read buffer will yield.
        """
        self._data = data
        self.data = data

        self.offset = 0
        self.length = len(data)

    cpdef void read(self, char* dest, int count) except *:
        """Reads ``count`` bytes into ``dest``.

        :param dest:
            Memory block to which the bytes will be written.
        :param int count:
            Number of bytes to read.
        :raises EndOfInputError:
            If the number of bytes available in the buffer is less than
            ``count``.
        """
        if count > self.length - self.offset:
            raise EndOfInputError(
                'Expected %d bytes but got %d bytes.' %
                (count, self.available)
            )

        memcpy(dest, self.data + self.offset, count)
        self.offset += count

    cpdef bytes take(self, int count):
        """Read the next ``count`` bytes from the buffer.

        :param int count:
            Number of bytes to read.
        :returns:
            ``bytes`` object containing exactly ``count`` bytes.
        :raises EndOfInputError:
            If the number of bytes available in the buffer is less than
            ``count``.
        """
        if count > self.length - self.offset:
            raise EndOfInputError(
                'Expected %d bytes but got %d bytes.' %
                (count, self.available)
            )

        cdef bytes result = self.data[self.offset:self.offset + count]
        self.offset += count

        return result

    property available:
        """Number of bytes available in the buffer."""

        def __get__(self):
            return self.length - self.offset
