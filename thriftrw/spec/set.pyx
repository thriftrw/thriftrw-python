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

from .base cimport TypeSpec
from thriftrw.wire cimport ttype
from thriftrw._cython cimport richcompare
from thriftrw.wire.value cimport SetValue
from thriftrw.wire.value cimport Value
from . cimport check

__all__ = ['SetTypeSpec']


cdef class SetTypeSpec(TypeSpec):
    """
    :param TypeSpec vspec:
        TypeSpec of values stored in the set.
    """

    ttype_code = ttype.SET

    def __init__(self, vspec):
        self.vspec = vspec
        self.linked = False

    cpdef TypeSpec link(self, scope):
        if not self.linked:
            self.linked = True
            self.vspec = self.vspec.link(scope)
        return self

    @property
    def name(self):
        return 'set<%s>' % self.vspec.name

    cpdef Value to_wire(self, object value):
        items = []
        for v in value:
            items.append(self.vspec.to_wire(v))
        return SetValue(
            value_ttype=self.vspec.ttype_code,
            values=items,
        )

    cpdef object to_primitive(self, object value):
        items = []
        for x in value:
            items.append(self.vspec.to_primitive(x))
        return items

    cpdef object from_wire(self, Value wire_value):
        check.type_code_matches(self, wire_value)
        result = set()
        for v in wire_value.values:
            result.add(self.vspec.from_wire(v))
        return result

    cpdef object from_primitive(self, object prim_value):
        result = set()
        for v in prim_value:
            result.add(self.vspec.from_primitive(v))
        return result

    cpdef void validate(self, object instance) except *:
        check.isiterable(self, instance)
        for v in instance:
            self.vspec.validate(v)

    def __str__(self):
        return 'SetTypeSpec(vspec=%r)' % self.vspec

    def __repr__(self):
        return str(self)

    def __richcmp__(SetTypeSpec self, SetTypeSpec other not None, int op):
        return richcompare(op, [
            (self.vspec, other.vspec),
        ])

