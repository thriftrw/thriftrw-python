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

from thriftrw import spec
from thriftrw.spec.spec_mapper import type_spec_or_ref

from .exceptions import ThriftCompilerError


__all__ = ['Generator']


class Generator(object):
    """Implements the Generate step of the compiler.

    During the Generate step, the system goes through the Thrift AST and
    collects all constants, and builds up type specs and classes with
    references to each other.
    """

    __slots__ = ('scope', 'type_mapper')

    def __init__(self, scope):
        """Initialize the generator.

        :param thriftrw.compile.scope.Scope scope:
            Scope maintaining the current compilation state.
        """
        self.scope = scope

    def process(self, definition):
        """Process the given definition from the AST.

        :param definition:
            A definition from the AST.
        """
        definition.apply(self)

    def visit_const(self, const):
        # TODO validate that const.name is a valid python identifier.

        typ = type_spec_or_ref(const.value_type)
        value = self.scope.resolve_const_value(const.value)

        if False and not typ.matches(value):
            # TODO implement typ.matches -- assuming we want to do validation
            raise ThriftCompilerError(
                'Value for constant "%s" on line %d does not match its type.'
                % (const.name, const.lineno)
            )
            # TODO Support constants which use typedefs of primitve types.

        self.scope.add_constant(const.name, value, const.lineno)

    def visit_typedef(self, typedef):
        self.scope.add_type_spec(
            typedef.name,
            spec.TypedefTypeSpec.compile(typedef),
            typedef.lineno,
        )

    def visit_enum(self, enum):
        enum_spec = spec.EnumTypeSpec.compile(enum)
        for key, value in enum_spec.items.items():
            self.scope.add_constant(
                name=enum_spec.name + '.' + key,
                value=value,
                lineno=enum.lineno,
                add_to_module=False
            )
        self.scope.add_type_spec(enum.name, enum_spec, enum.lineno)
        # TODO Add type_spec to list of reserved words.

    def visit_struct(self, struct):
        struct_spec = spec.StructTypeSpec.compile(struct)
        self.scope.add_type_spec(struct_spec.name, struct_spec, struct.lineno)

    def visit_union(self, union):
        union_spec = spec.UnionTypeSpec.compile(union)
        self.scope.add_type_spec(union_spec.name, union_spec, union.lineno)

    def visit_exc(self, exc):
        exc_spec = spec.ExceptionTypeSpec.compile(exc)
        self.scope.add_type_spec(exc_spec.name, exc_spec, exc.lineno)

    def visit_service(self, svc):
        service_spec = spec.ServiceSpec.compile(svc)
        self.scope.add_service_spec(service_spec)
