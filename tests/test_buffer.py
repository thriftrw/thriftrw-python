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

import pytest

from thriftrw._buffer import ReadBuffer
from thriftrw._buffer import WriteBuffer
from thriftrw.errors import EndOfInputError


def test_empty_write_buffer():
    buff = WriteBuffer(10)
    assert buff.length == 0
    assert buff.capacity == 10
    assert buff.value == b''


def test_empty_read_buffer():
    buff = ReadBuffer(b'')
    assert buff.take(0) == b''

    with pytest.raises(EndOfInputError):
        buff.take(1)


def test_simple_write():
    buff = WriteBuffer(10)
    buff.write_bytes(b'hello ')
    buff.write_bytes(b'world')

    assert buff.value == b'hello world'
    assert buff.length == 11


def test_simple_read():
    buff = ReadBuffer(b'abcd')

    assert buff.take(1) == b'a'
    assert buff.take(2) == b'bc'

    with pytest.raises(EndOfInputError):
        buff.take(2)

    assert buff.take(1) == b'd'


def test_write_clear():
    buff = WriteBuffer(10)
    buff.write_bytes(b'foo')
    buff.clear()

    assert buff.value == b''
    assert buff.capacity == 10
    assert buff.length == 0
