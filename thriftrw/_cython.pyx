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


cdef bint richcompare_op(int op, int compare):
    # op    operation
    # 0     <
    # 1     <=
    # 2     ==
    # 3     !=
    # 4     >
    # 5     >=

    if op == 2:
        return compare == 0
    elif op == 3:
        return compare != 0
    elif op == 4:
        return compare > 0
    elif op == 5:
        return compare >= 0
    elif op == 0:
        return compare < 0
    elif op == 1:
        return compare <= 0
    else:
        assert False, 'Invalid comparison operator "%d"' % (op,)


cdef bint richcompare(int op, list pairs):
    """Utility function to make ``richcmp`` easier to write.

    It takes a list of attribute pairs. Attributes are compared in the order
    they appear and the result is returned based on the ``op``.

    .. code-block:: python

        def __richcmp__(self, other, op):
            return richcompare(
                op,
                [
                    (self.attr1, other.attr1),
                    (self.attr2, other.attr2),
                    # ...
                ]
            )
    """

    cdef int compare = 0

    for (left, right) in pairs:
        if left > right:
            compare = 1
            break
        elif left < right:
            compare = -1
            break

    return richcompare_op(op, compare)
