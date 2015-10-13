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

import collections

from thriftrw.wire import TType
from thriftrw.wire.value import ListValue

from . import check
from .base import TypeSpec

__all__ = ['ListTypeSpec']


class ListTypeSpec(TypeSpec):
    """Spec for list types."""

    __slots__ = ('vspec', 'linked')

    ttype_code = TType.LIST
    surface = list

    def __init__(self, vspec):
        """
        :param TypeSpec vspec:
            TypeSpec of values stored in the list.
        """

        #: TypeSpec for the kind of values lists conforming to this spec can
        #: contain.
        self.vspec = vspec
        self.linked = False

    def link(self, scope):
        if not self.linked:
            self.linked = True
            self.vspec = self.vspec.link(scope)
        return self

    @property
    def name(self):
        return 'list<%s>' % self.vspec.name

    def to_wire(self, value):
        return ListValue(
            value_ttype=self.vspec.ttype_code,
            values=[self.vspec.to_wire(v) for v in value],
        )

    def to_primitive(self, value):
        return [self.vspec.to_primitive(x) for x in value]

    def from_wire(self, wire_value):
        check.type_code_matches(self, wire_value)
        return [self.vspec.from_wire(v) for v in wire_value.values]

    def from_primitive(self, prim_value):
        return [self.vspec.from_primitive(v) for v in prim_value]

    def validate(self, instance):
        check.instanceof_class(self, collections.Sequence, instance)
        for v in instance:
            self.vspec.validate(v)

    def __str__(self):
        return 'ListTypeSpec(vspec=%r)' % self.vspec

    __repr__ = __str__

    def __eq__(self, other):
        return (
            self.vspec == other.vspec and
            self.linked == other.linked
        )
