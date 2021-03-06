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

from thriftrw._cython cimport richcompare
from thriftrw.wire.value cimport Value

from .base cimport TypeSpec

__all__ = ['TypeReference']


cdef class TypeReference(TypeSpec):
    """A reference to another type."""

    __slots__ = ('name', 'lineno')

    def __init__(self, name, lineno):
        self.name = str(name)
        self.lineno = lineno

    cpdef TypeSpec link(self, scope):
        return scope.resolve_type_spec(self.name, self.lineno)

    # It may be worth making this implement the TypeSpec interface and raise
    # exceptions complaining about unresolved type references, since that's
    # probably a bug.

    def __str__(self):
        return 'TypeReference(%s, lineno=%d)' % (
            self.name, self.lineno
        )

    def __repr__(self):
        return str(self)

    def __richcmp__(TypeReference self, TypeReference other not None, int op):
        return richcompare(op, [
            (self.name, other.name),
            (self.lineno, other.lineno),
        ])
