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


class Scope(object):

    __slots__ = ('constants', 'types', 'services')

    def __init__(self):
        self.constants = {}
        self.types = {}
        self.services = {}

    def __str__(self):
        return "Scope(constants=%r, types=%r, services=%r)" % (
            self.constants, self.types, self.services
        )

    __repr__ = __str__

    def add_constant(self, name, value, lineno):
        assert value is not None

        if name in self.constants:
            raise ThriftCompilerError(
                'Cannot define constant "%s" at line %d. '
                'That name is already taken.'
                % (name, lineno)
            )

        self.constants[name] = value

    def add_type(self, name, typ, lineno):
        assert type is not None

        if name in self.types:
            raise ThriftCompilerError(
                'Cannot define type "%s" at line %d. '
                'Another type with that name already exists.'
                % (name, lineno)
            )

        self.types[name] = typ


class TypeMapper(object):

    def get(self, typ):
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


class ConstValueResolver(object):

    def __init__(self, scope):
        self.scope = scope

    def resolve(self, const_value):
        return const_value.apply(self)

    def visit_primitive(self, const):
        return const.value

    def visit_reference(self, const):
        value = self.scope.constants.get(const.name)
        if value is None:
            raise ThriftCompilerError(
                'Unknown constant "%s" referenced at line %d'
                % (const.name, const.lineno)
            )
        return value


class Compiler(object):

    def __init__(self):
        self.scope = Scope()
        self.types = TypeMapper()
        self.values = ConstValueResolver(self.scope)

    def compile(self, program):
        for header in program.headers:
            header.apply(self)

        for definition in program.definitions:
            definition.apply(self)

        scope = self.scope
        for name in scope.types.keys():
            scope.types[name] = scope.types[name].link(scope)

    def visit_include(self, include):
        raise ThriftCompilerError(
            'Include of "%s" found on line %d. '
            'thriftrw does not support including other Thrift files.'
            % (include.path, include.lineno)
        )

    def visit_namespace(self, namespace):
        pass  # nothing to do

    def visit_const(self, const):
        typ = self.types.get(const.value_type)
        value = self.values.resolve(const.value)

        # TODO Implement typ.matches
        if False and not typ.matches(value):
            raise ThriftCompilerError(
                'Value %r for constant %s at line %d does not match its type.'
                % (value, const.name, const.lineno)
            )

        self.scope.add_constant(const.name, value, const.lineno)

    def visit_typedef(self, typedef):
        target = self.types.get(typedef.target_type)
        self.scope.add_type(typedef.name, target, typedef.lineno)

    def visit_enum(self, enum):
        items = {}

        prev = -1
        for item in enum.items:
            value = item.value
            if value is None:
                value = prev + 1
            prev = value
            items[item.name] = value

            # Make the enum value available as a constant under the name
            # <enum name>.<value name>
            self.scope.add_constant(
                '%s.%s' % (enum.name, item.name), value, item.lineno
            )

        self.scope.add_type(enum.name, types.I32Type(), enum.lineno)
        raise NotImplementedError  # TODO generate class

    def visit_struct(self, struct):
        fields = deque()

        for field in struct.fields:
            fields.append(self._mk_field(struct, field))

        cls = None  # TODO generate class
        raise NotImplementedError

        self.scope.add_type(
            struct.name, types.StructType(cls, fields), struct.lineno
        )

    def visit_union(self, union):
        fields = deque()

        for field in union.fields:
            fields.append(self._mk_field(union, field))

        cls = None  # TODO generate class
        raise NotImplementedError

        self.scope.add_type(
            union.name, types.StructType(cls, fields), union.lineno
        )

    def visit_exc(self, exc):
        fields = deque()

        for field in exc.fields:
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

        if field.requiredness is None:
            raise ThriftCompilerError(
                'Field %s of %s does not explicitly specify requiredness. '
                'Please specify whether the field is required or optional.'
                % (field.name, struct.name)
            )

        ftype = self.types.get(field.field_type)
        return types.Field(id=field.id, name=field.name, ftype=ftype)


# Reserved identifiers
# TODO forbid declared items from using these names
RESERVED = frozenset((
    'BEGIN',
    'END',
    '__CLASS__',
    '__DIR__',
    '__FILE__',
    '__FUNCTION__',
    '__LINE__',
    '__METHOD__',
    '__NAMESPACE__',
    'abstract',
    'alias',
    'and',
    'args',
    'as',
    'async',
    'assert',
    'await',
    'begin',
    'break',
    'case',
    'catch',
    'class',
    'clone',
    'continue',
    'declare',
    'def',
    'default',
    'del',
    'delete',
    'do',
    'dynamic',
    'elif',
    'else',
    'elseif',
    'elsif',
    'end',
    'enddeclare',
    'endfor',
    'endforeach',
    'endif',
    'endswitch',
    'endwhile',
    'ensure',
    'except',
    'exec',
    'finally',
    'float',
    'for',
    'foreach',
    'function',
    'global',
    'goto',
    'if',
    'implements',
    'import',
    'in',
    'inline',
    'instanceof',
    'interface',
    'is',
    'lambda',
    'module',
    'native',
    'new',
    'next',
    'nil',
    'not',
    'or',
    'pass',
    'public',
    'print',
    'private',
    'protected',
    'public',
    'raise',
    'redo',
    'rescue',
    'retry',
    'register',
    'return',
    'self',
    'sizeof',
    'static',
    'super',
    'switch',
    'synchronized',
    'then',
    'this',
    'throw',
    'transient',
    'try',
    'undef',
    'union',
    'unless',
    'unsigned',
    'until',
    'use',
    'var',
    'virtual',
    'volatile',
    'when',
    'while',
    'with',
    'xor',
    'yield'
))
