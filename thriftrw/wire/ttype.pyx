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

"""
Different TType codes supported by Thrift.

.. py:data:: BOOL
    :annotation: = 2

.. py:data:: BYTE
    :annotation: = 3

.. py:data:: DOUBLE
    :annotation: = 4

.. py:data:: I16
    :annotation: = 6

.. py:data:: I32
    :annotation: = 8

.. py:data:: I64
    :annotation: = 10

.. py:data:: BINARY
    :annotation: = 11

.. py:data:: STRUCT
    :annotation: = 12

.. py:data:: MAP
    :annotation: = 13

.. py:data:: SET
    :annotation: = 14

.. py:data:: LIST
    :annotation: = 15

"""

from __future__ import absolute_import, unicode_literals, print_function


cpdef str name_of(int value):
    """Returns the name of the TType with the given value.

    Returns None if no such TType exists.
    """
    if value == TType.BOOL:
        return str('BOOL')
    elif value == TType.BYTE:
        return str('BYTE')
    elif value == TType.DOUBLE:
        return str('DOUBLE')
    elif value == TType.I16:
        return str('I16')
    elif value == TType.I32:
        return str('I32')
    elif value == TType.I64:
        return str('I64')
    elif value == TType.BINARY:
        return str('BINARY')
    elif value == TType.STRUCT:
        return str('STRUCT')
    elif value == TType.MAP:
        return str('MAP')
    elif value == TType.SET:
        return str('SET')
    elif value == TType.LIST:
        return str('LIST')
    else:
        return None
