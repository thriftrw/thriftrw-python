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


cpdef str name_of(int value):
    """Returns the name of the TType with the given value.

    Returns None if no such TType exists.
    """
    if value == 2:
        return str('BOOL')
    elif value == 3:
        return str('BYTE')
    elif value == 4:
        return str('DOUBLE')
    elif value == 6:
        return str('I16')
    elif value == 8:
        return str('I32')
    elif value == 10:
        return str('I64')
    elif value == 11:
        return str('BINARY')
    elif value == 12:
        return str('STRUCT')
    elif value == 13:
        return str('MAP')
    elif value == 14:
        return str('SET')
    elif value == 15:
        return str('LIST')
    else:
        return None
