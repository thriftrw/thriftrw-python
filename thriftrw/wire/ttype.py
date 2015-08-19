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

from collections import namedtuple

__all__ = ['TType']

_TType = namedtuple(
    '_TType',
    'BOOL BYTE DOUBLE I16 I32 I64 BINARY STRUCT MAP SET LIST'
)

#: Different TType codes supported by Thrift.
#:
#: .. autoattribute:: TType.BOOL
#:
#: .. autoattribute:: TType.BYTE
#:
#: .. autoattribute:: TType.DOUBLE
#:
#: .. autoattribute:: TType.I16
#:
#: .. autoattribute:: TType.I32
#:
#: .. autoattribute:: TType.I64
#:
#: .. autoattribute:: TType.BINARY
#:
#: .. autoattribute:: TType.STRUCT
#:
#: .. autoattribute:: TType.MAP
#:
#: .. autoattribute:: TType.SET
#:
#: .. autoattribute:: TType.LIST
#:
TType = _TType(
    BOOL=2,
    BYTE=3,
    DOUBLE=4,
    I16=6,
    I32=8,
    I64=10,
    BINARY=11,
    STRUCT=12,
    MAP=13,
    SET=14,
    LIST=15,
)
