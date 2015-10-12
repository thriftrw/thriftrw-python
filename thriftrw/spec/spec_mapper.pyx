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

from .reference import TypeReference
from .map import MapTypeSpec
from .set import SetTypeSpec
from .list import ListTypeSpec
from .primitive import (
    BoolTypeSpec,
    ByteTypeSpec,
    DoubleTypeSpec,
    I16TypeSpec,
    I32TypeSpec,
    I64TypeSpec,
    BinaryTypeSpec,
    TextTypeSpec,
)


__slots__ = ['type_spec_or_ref']


#: Mapping of Thrift primitive type names to corresponding type specs.
PRIMITIVE_TYPES = {
    'bool': BoolTypeSpec,
    'byte': ByteTypeSpec,
    'double': DoubleTypeSpec,
    'i16': I16TypeSpec,
    'i32': I32TypeSpec,
    'i64': I64TypeSpec,
    'string': TextTypeSpec,
    'binary': BinaryTypeSpec,
}


class TypeSpecMapper(object):
    """Maps AST types to type specifications.

    For references to defined types, return ``TypeReference`` objects instead.
    These will be replaced during the linking stage.
    """

    __slots__ = ()

    def get(self, typ):
        """Get the TypeSpec for the given AST type.

        If the type being referenced is a custom defined type, a TypeReference
        is returned instead.
        """
        return typ.apply(self)

    def visit_defined(self, typ):
        return TypeReference(typ.name, typ.lineno)

    def visit_primitive(self, typ):
        assert typ.name in PRIMITIVE_TYPES
        return PRIMITIVE_TYPES[typ.name]

    def visit_map(self, mtype):
        kspec = self.get(mtype.key_type)
        vspec = self.get(mtype.value_type)
        return MapTypeSpec(kspec, vspec)

    def visit_set(self, stype):
        vspec = self.get(stype.value_type)
        return SetTypeSpec(vspec)

    def visit_list(self, ltype):
        vspec = self.get(ltype.value_type)
        return ListTypeSpec(vspec)


#: Gets a TypeSpec for the given type if it's a native Thrift type or a
#: TypeReference if it's a custom defined type.
type_spec_or_ref = TypeSpecMapper().get
