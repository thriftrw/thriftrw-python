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

import six
from collections import deque

from thriftrw.idl import ast

from . import gen
from . import spec
from .const import ConstValueResolver
from .exceptions import ThriftCompilerError


#: Mapping of Thrift primitive type names to corresponding type specs.
PRIMITIVE_TYPES = {
    'bool': spec.BoolTypeSpec,
    'byte': spec.ByteTypeSpec,
    'double': spec.DoubleTypeSpec,
    'i16': spec.I16TypeSpec,
    'i32': spec.I32TypeSpec,
    'i64': spec.I64TypeSpec,
    'string': spec.TextTypeSpec,
    'binary': spec.BinaryTypeSpec,
}


class TypeMapper(object):
    """Maps AST types to type specifications."""

    __slots__ = ()

    def get(self, typ):
        """Get the TypeSpec for the given AST type.

        If the type being referenced is a custom defined type, a TypeReference
        is returned instead.
        """
        return typ.apply(self)

    def visit_defined(self, typ):
        return spec.TypeReference(typ.name, typ.lineno)

    def visit_primitive(self, typ):
        assert typ.name in PRIMITIVE_TYPES
        return PRIMITIVE_TYPES[typ.name]

    def visit_map(self, mtype):
        kspec = self.get(mtype.key_type)
        vspec = self.get(mtype.value_type)
        return spec.MapTypeSpec(kspec, vspec)

    def visit_set(self, stype):
        vspec = self.get(stype.value_type)
        return spec.SetTypeSpec(vspec)

    def visit_list(self, ltype):
        vspec = self.get(ltype.value_type)
        return spec.ListTypeSpec(vspec)


class Gatherer(object):
    """Implements the Gather step of the compiler.

    During the Gather step, the system goes through the Thrift AST and
    collects all constants and definitions that will be defined.
    """

    __slots__ = ('scope', 'type_mapper', 'const_resolver')

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
                'Value for constant "%s" on line %d does not match its type.'
                % (const.name, const.lineno)
            )
            # TODO Support constants which use typedefs of primitve types.

        self.scope.add_constant(const.name, value, const.lineno)

    def visit_typedef(self, typedef):
        target = self.type_mapper.get(typedef.target_type)
        self.scope.add_type_spec(typedef.name, target, typedef.lineno)

    def visit_enum(self, enum):
        enum_spec = spec.I32TypeSpec
        self.scope.add_type_spec(enum.name, enum_spec, enum.lineno)
        self.scope.add_class(gen.enum_cls(enum, enum_spec))

        # TODO Add type_spec to list of reserved words.

    def visit_struct(self, struct):
        fields = deque()

        for field in struct.fields:
            fields.append(self._mk_field(struct.name, field))

        struct_cls = gen.struct_cls(
            struct.name, struct.fields, None, self.const_resolver
        )
        struct_spec = spec.StructTypeSpec(struct.name, struct_cls, fields)
        struct_cls.type_spec = struct_spec

        self.scope.add_type_spec(struct.name, struct_spec, struct.lineno)
        self.scope.add_class(struct_cls)

    def visit_union(self, union):
        fields = deque()

        for field in union.fields:

            if field.default is not None:
                raise ThriftCompilerError(
                    'Field "%s" of union "%s" has a default value. '
                    'Fields of unions cannot have default values. '
                    % (field.name, union.name)
                )

            fields.append(self._mk_field(union.name, field))

        union_cls = gen.union_cls(union.name, union.fields, None)
        union_spec = spec.StructTypeSpec(union.name, union_cls, fields)
        union_cls.type_spec = union_spec

        self.scope.add_type_spec(union.name, union_spec, union.lineno)
        self.scope.add_class(union_cls)

    def visit_exc(self, exc):
        fields = deque()

        for field in exc.fields:
            fields.append(self._mk_field(exc.name, field))

        exc_cls = gen.exception_cls(
            exc.name, exc.fields, None, self.const_resolver
        )
        exc_spec = spec.StructTypeSpec(exc.name, exc_cls, fields)
        exc_cls.type_spec = exc_spec

        self.scope.add_type_spec(exc.name, exc_spec, exc.lineno)
        self.scope.add_class(exc_cls)

    def visit_service(self, svc):
        function_specs = deque()

        for func in svc.functions:

            if func.oneway:
                raise ThriftCompilerError(
                    'Function "%s.%s" is oneway. '
                    'Oneway functions are not supported by thriftrw.'
                    % (svc_ast.name, func.name)
                )

            args_name = str('%s_%s_request' % (svc.name, func.name))
            param_specs = deque()
            for param in func.parameters:
                # TODO decide correct behavior for when requiredness is
                # specified on parameters
                param_specs.append(self._mk_field(args_name, param))

            args_cls = gen.struct_cls(
                args_name,
                func.parameters,
                None,
                self.const_resolver,
                require_requiredness=False,
            )
            args_spec = spec.StructTypeSpec(args_name, args_cls, param_specs)
            args_cls.type_spec = args_spec

            result_name = str('%s_%s_response' % (svc.name, func.name))
            result_fields = deque()
            result_specs = deque()

            if func.return_type is not None:
                # Generate a fake AST node
                return_field = ast.Field(
                    id=0,
                    name='success',
                    field_type=func.return_type,
                    requiredness=None,
                    default=None,
                    annotations=None,
                    lineno=func.lineno,
                )

                result_fields.append(return_field)
                result_specs.append(
                    self._mk_field(result_name, return_field)
                )

            for exc in func.exceptions:

                if exc.requiredness is not None:
                    raise ThriftCompilerError(
                        'Exception "%s" of "%s" is "%s". '
                        'Exceptions cannot be specified as required or optional.'
                        % (exc.name, func.name,
                           'required' if exc.requiredness else 'optional')
                    )

                if exc.default is not None:
                    raise ThriftCompilerError(
                        'Exception "%s" of "%s" has a default value. '
                        'Exceptions cannot have default values.'
                        % (exc.name, func.name,
                           'required' if exc.requiredness else 'optional')
                    )

                result_fields.append(exc)
                result_specs.append(self._mk_field(result_name, exc))

            result_cls = gen.union_cls(
                result_name,
                result_fields,
                None,
            )
            result_spec = spec.StructTypeSpec(
                result_name, result_cls, result_specs
            )
            result_cls.type_spec = result_spec

            self.scope.add_class(args_cls)
            self.scope.add_class(result_cls)

            function_specs.append(
                spec.FunctionSpec(
                    func.name,
                    args_spec=args_spec,
                    result_spec=result_spec,
                )
            )

        self.scope.add_service_spec(
            spec.ServiceSpec(svc.name, function_specs, svc.parent)
        )

    def _mk_field(self, container_name, field):
        if field.id is None:
            raise ThriftCompilerError(
                'Field "%s" of "%s" does not have an explicit field ID. '
                'Please specify the numeric ID for the field.'
                % (field.name, container_name)
            )

        field_spec = self.type_mapper.get(field.field_type)
        return spec.FieldSpec(id=field.id, name=field.name, spec=field_spec)
