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

from collections import deque

from . import types
from .const import ConstValueResolver
from .exceptions import ThriftCompilerError


PRIMITIVE_TYPES = {
    'bool': types.BoolType,
    'byte': types.ByteType,
    'double': types.DoubleType,
    'i16': types.I16Type,
    'i32': types.I32Type,
    'i64': types.I64Type,
    'string': types.TextType,
    'binary': types.BinaryType,
}


class TypeMapper(object):
    """Maps AST types to type specifications."""

    __slots__ = ()

    def get(self, typ):
        """Get the Type specification for the given AST type.

        If the type being referenced is a custom defined type, a TypeReference
        is returned instead.
        """
        return typ.apply(self)

    def visit_defined(self, typ):
        return types.TypeReference(typ.name, typ.lineno)

    def visit_primitive(self, typ):
        assert typ.name in PRIMITIVE_TYPES
        return PRIMITIVE_TYPES[typ.name]

    def visit_map(self, mtype):
        ktype = self.get(mtype.key_type)
        vtype = self.get(mtype.value_type)
        return types.MapType(ktype, vtype)

    def visit_set(self, stype):
        vtype = self.get(stype.value_type)
        return types.SetType(vtype)

    def visit_list(self, ltype):
        vtype = self.get(ltype.value_type)
        return types.ListType(vtype)


class Gatherer(object):
    """Implements the Gather step of the compiler.

    During the Gather step, the system goes through the Thrift AST and
    collects all constants and definitions that will be defined.
    """

    __slots__ = ('scope', 'type_mapper')

    def __init__(self, scope):
        self.scope = scope
        self.type_mapper = TypeMapper()
        self.const_resolver = ConstValueResolver(scope)

    def gather(self, definition):
        definition.apply(self)

    def visit_const(self, const):
        # TODO validate that const.name is a valid python identifier.

        typ = self.type_mapper.get(const.value_type)
        value = self.const_resolver.resolve(const.value)

        if False and not typ.matches(value):
            # TODO implement typ.matches -- assuming we want to do validation
            raise ThriftCompilerError(
                'Value for constant %s on line %d does not match its type.'
                % (const.name, const.lineno)
            )
            # TODO Support constants which use typedefs of primitve types.

        self.scope.add_constant(const.name, value, const.lineno)

    def visit_typedef(self, typedef):
        target = self.type_mapper.get(typedef.target_type)
        self.scope.add_type(typedef.name, target, typedef.lineno)

    def visit_enum(self, enum):
        items = deque()

        prev = -1
        for item in enum.items:
            value = item.value
            if value is None:
                value = prev + 1
            prev = value
            item = item._replace(value=value)
            items.append(item)

        enum = enum._replace(items=items)
        self.scope.add_type(enum.name, types.I32Type, enum.lineno)

        # TODO Add type_spec to list of reserved words.
        # TODO Find better name for type_spec
        # items['type_spec'] = types.I32Type

        raise NotImplementedError  # TODO generate class

    def visit_struct(self, struct):
        fields = deque()

        for field in struct.fields:

            if field.requiredness is None:
                raise ThriftCompilerError(
                    'Field %s of %s does not explicitly specify requiredness. '
                    'Please specify whether the field is required or optional.'
                    % (field.name, struct.name)
                )

            fields.append(self._mk_field(struct, field))

        cls = None  # TODO generate class
        raise NotImplementedError

        self.scope.add_type(
            struct.name, types.StructType(cls, fields), struct.lineno
        )

    def visit_union(self, union):
        fields = deque()

        for field in union.fields:

            if field.default is not None:
                raise ThriftCompilerError(
                    'Field %s of union %s has a default value. '
                    'Fields of unions cannot have default values. '
                    % (field.name, union.name)
                )

            fields.append(self._mk_field(union, field))

        cls = None  # TODO generate class
        raise NotImplementedError

        self.scope.add_type(
            union.name, types.StructType(cls, fields), union.lineno
        )

    def visit_exc(self, exc):
        fields = deque()

        for field in exc.fields:

            if field.requiredness is None:
                raise ThriftCompilerError(
                    'Field %s of %s does not explicitly specify requiredness. '
                    'Please specify whether the field is required or optional.'
                    % (field.name, exc.name)
                )

            fields.append(self._mk_field(exc, field))

        cls = None  # TODO generate class
        raise NotImplementedError

        self.scope.add_type(
            exc.name, types.StructType(cls, fields), exc.lineno
        )

    def visit_service(self, svc):
        raise NotImplementedError

    def _mk_field(self, struct, field):
        if field.id is None:
            raise ThriftCompilerError(
                'Field %s of %s does not have an explicit field ID. '
                'Please specify the numeric ID for the field.'
                % (field.name, struct.name)
            )

        ftype = self.type_mapper.get(field.field_type)
        return types.Field(id=field.id, name=field.name, ftype=ftype)
