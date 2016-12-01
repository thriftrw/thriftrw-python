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
from thriftrw.wire.value cimport ListValue
from thriftrw.wire.value cimport Value
from thriftrw.protocol.core cimport ListHeader, ProtocolWriter, ProtocolReader

__all__ = ['ListTypeSpec']


cdef class ListTypeSpec(TypeSpec):
    """Spec for list types.

    .. py:attribute:: vspec

        TypeSpec for the kind of values lists conforming to this spec must
        contain.
    """

    surface = list

    def __init__(self, vspec):
        """
        :param TypeSpec vspec:
            TypeSpec of values stored in the list.
        """
        self.ttype_code = ttype.LIST
        self.vspec = vspec
        self.linked = False

    cpdef TypeSpec link(self, scope):
        if not self.linked:
            self.linked = True
            self.vspec = self.vspec.link(scope)
        return self

    @property
    def name(self):
        return 'list<%s>' % self.vspec.name

    cpdef object read_from(ListTypeSpec self, ProtocolReader reader):
        cdef ListHeader header = reader.read_list_begin()
        cdef list output = []
        for i in range(header.size):
            output.append(self.vspec.read_from(reader))

        reader.read_list_end()
        return output

    cpdef Value to_wire(ListTypeSpec self, object value):
        return ListValue(
            value_ttype=self.vspec.ttype_code,
            values=[self.vspec.to_wire(v) for v in value],
        )

    cpdef object to_primitive(ListTypeSpec self, object value):
        return [self.vspec.to_primitive(x) for x in value]

    cpdef void write_to(ListTypeSpec self, ProtocolWriter writer,
                        object value) except *:
        cdef ListHeader header = ListHeader(self.vspec.ttype_code, len(value))
        writer.write_list_begin(header)
        for v in value:
            self.vspec.write_to(writer, v)
        writer.write_list_end()

    cpdef object from_wire(ListTypeSpec self, Value wire_value):
        check.type_code_matches(self, wire_value)
        return [self.vspec.from_wire(v) for v in wire_value.values]

    cpdef object from_primitive(ListTypeSpec self, object prim_value):
        return [self.vspec.from_primitive(v) for v in prim_value]

    cpdef void validate(ListTypeSpec self, object instance) except *:
        check.isiterable(self, instance)
        for v in instance:
            self.vspec.validate(v)

    def __str__(self):
        return 'ListTypeSpec(vspec=%r)' % self.vspec

    def __repr__(self):
        return str(self)

    def __richcmp__(ListTypeSpec self, ListTypeSpec other not None, int op):
        return richcompare(op, [
            (self.vspec, other.vspec),
        ])

