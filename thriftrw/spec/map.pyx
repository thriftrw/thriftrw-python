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

from . cimport check
from .base cimport TypeSpec
from thriftrw.wire cimport ttype
from thriftrw._cython cimport richcompare
from thriftrw.wire.value cimport MapItem, MapValue, Value
from thriftrw.protocol.core cimport MapHeader, ProtocolWriter, ProtocolReader

__all__ = ['MapTypeSpec']


cdef class MapTypeSpec(TypeSpec):
    """Spec for map types.

    .. py:attribute:: kspec

        TypeSpec for the kind of keys matching maps must contain.

    .. py:attribute:: vspec

        TypeSpec for the kind of values matching maps must contain.
    """

    surface = dict

    def __init__(self, kspec, vspec):
        """
        :param TypeSpec kspec:
            TypeSpec of the keys in the map.
        :param TypeSpec vspec:
            TypeSpec of the values in the map.
        """
        self.ttype_code = ttype.MAP
        self.kspec = kspec
        self.vspec = vspec
        self.linked = False

    @property
    def name(self):
        return 'map<%s, %s>' % (self.kspec.name, self.vspec.name)

    cpdef TypeSpec link(self, scope):
        if not self.linked:
            self.linked = True
            self.kspec = self.kspec.link(scope)
            self.vspec = self.vspec.link(scope)
        return self

    cpdef Value to_wire(MapTypeSpec self, object value):
        return MapValue(
            key_ttype=self.kspec.ttype_code,
            value_ttype=self.vspec.ttype_code,
            pairs=[
                MapItem(self.kspec.to_wire(k), self.vspec.to_wire(v))
                for k, v in value.items()
            ]
        )

    cpdef object to_primitive(MapTypeSpec self, object value):
        return {
            self.kspec.to_primitive(k): self.vspec.to_primitive(v)
            for k, v in value.items()
        }

    cpdef object read_from(MapTypeSpec self, ProtocolReader reader):
        cdef MapHeader header = reader.read_map_begin()
        cdef dict output = {
            self.kspec.read_from(reader): self.vspec.read_from(reader)
            for i in range(header.size)
        }
        reader.read_map_end()
        return output

    cpdef void write_to(MapTypeSpec self, ProtocolWriter writer,
                        object value) except *:
        cdef MapHeader header = MapHeader(
            self.kspec.ttype_code, self.vspec.ttype_code, len(value)
        )
        writer.write_map_begin(header)
        for k, v in value.items():
            self.kspec.write_to(writer, k)
            self.vspec.write_to(writer, v)
        writer.write_map_end()

    cpdef object from_wire(MapTypeSpec self, Value wire_value):
        check.type_code_matches(self, wire_value)
        return {
            self.kspec.from_wire(i.key): self.vspec.from_wire(i.value)
            for i in wire_value.pairs
        }

    cpdef object from_primitive(MapTypeSpec self, object prim_value):
        return {
            self.kspec.from_primitive(k): self.vspec.from_primitive(v)
            for k, v in prim_value.items()
        }

    cpdef void validate(MapTypeSpec self, object instance) except *:
        check.ismapping(self, instance)
        for k, v in instance.items():
            self.kspec.validate(k)
            self.vspec.validate(v)

    def __str__(self):
        return 'MapTypeSpec(kspec=%r, vspec=%r)' % (self.kspec, self.vspec)

    def __repr__(self):
        return str(self)

    def __richcmp__(MapTypeSpec self, MapTypeSpec other not None, int op):
        return richcompare(op, [
            (self.kspec, other.kspec),
            (self.vspec, other.vspec),
        ])

