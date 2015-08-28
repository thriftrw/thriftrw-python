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
from thriftrw.wire.value import MapValue

from . import check
from .base import TypeSpec

__all__ = ['MapTypeSpec']


class MapTypeSpec(TypeSpec):
    """Spec for map types."""

    __slots__ = ('kspec', 'vspec', 'linked')

    ttype_code = TType.MAP
    surface = dict

    def __init__(self, kspec, vspec):
        """
        :param TypeSpec kspec:
            TypeSpec of the keys in the map.
        :param TypeSpec vspec:
            TypeSpec of the values in the map.
        """

        #: TypeSpec for the kind of keys matching maps can contain.
        self.kspec = kspec

        #: TypeSpec for the kind of values matching maps can contain.
        self.vspec = vspec

        self.linked = False

    @property
    def name(self):
        return 'map<%s, %s>' % (self.kspec.name, self.vspec.name)

    def link(self, scope):
        if not self.linked:
            self.linked = True
            self.kspec = self.kspec.link(scope)
            self.vspec = self.vspec.link(scope)
        return self

    def to_wire(self, value):
        check.instanceof_class(self, collections.Mapping, value)
        return MapValue(
            key_ttype=self.kspec.ttype_code,
            value_ttype=self.vspec.ttype_code,
            pairs=[
                (self.kspec.to_wire(k), self.vspec.to_wire(v))
                for k, v in value.items()
            ]
        )

    def from_wire(self, wire_value):
        check.type_code_matches(self, wire_value)
        return {
            self.kspec.from_wire(k): self.vspec.from_wire(v)
            for k, v in wire_value.pairs
        }

    def __str__(self):
        return 'MapTypeSpec(kspec=%r, vspec=%r)' % (self.kspec, self.vspec)

    __repr__ = __str__

    def __eq__(self, other):
        return (
            self.kspec == other.kspec and
            self.vspec == other.vspec and
            self.linked == other.linked
        )
