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

import types

from ..errors import ThriftCompilerError

__all__ = ['Scope']


class Scope(object):
    """Maintains the compilation state across steps.

    The scope is not exported to the user directly. It's only used to maintain
    state of known types and values during the compilation process and holds a
    reference to the final generated module.
    """

    __slots__ = ('const_specs', 'type_specs', 'module', 'service_specs', 'include_scopes')

    def __init__(self, name):
        """Initialize the scope.

        :param name:
            Name of the generated module.
        """
        self.type_specs = {}
        self.const_specs = {}
        self.service_specs = {}
        self.include_scopes = {}

        self.module = types.ModuleType(str(name))
        self.module.scope = self

    def __str__(self):
        return "Scope(%r)" % {
            'const_specs': self.const_specs,
            'type_specs': self.type_specs,
            'service_specs': self.service_specs,
            'module': self.module,
        }

    __repr__ = __str__

    def _resolve_nested(self, name, lineno, specs_name, type_name):
        if '.' in name:
            include, spec_name = name.split('.', 1)
            if include in self.include_scopes:
                scope = self.include_scopes[include]
                return scope._resolve_nested(spec_name, lineno, specs_name, type_name).link(self)

        specs = getattr(self, specs_name)
        if name not in specs:
            raise ThriftCompilerError(
                'Unknown %s "%s" referenced at line %d' % (type_name, name, lineno)
            )
        return specs[name].link(self)

    def resolve_const_spec(self, name, lineno):
        """Finds and links the ConstSpec with the given name."""
        return self._resolve_nested(name, lineno, 'const_specs', 'constant')

    def resolve_type_spec(self, name, lineno):
        """Finds and links the TypeSpec with the given name."""
        return self._resolve_nested(name, lineno, 'type_specs', 'type')

    def add_service_spec(self, service_spec):
        """Registers the given ``ServiceSpec`` into the scope.

        Raises ``ThriftCompilerError`` if the name has already been used.
        """
        assert service_spec is not None

        if service_spec.name in self.service_specs:
            raise ThriftCompilerError(
                'Cannot define service "%s". That name is already taken.'
                % service_spec.name
            )
        self.service_specs[service_spec.name] = service_spec

    def add_const_spec(self, const_spec):
        """Adds a ConstSpec to the compliation scope.

        If the ConstSpec's ``save`` attribute is True, the constant will be
        added to the module at the top-level.
        """
        if const_spec.name in self.const_specs:
            raise ThriftCompilerError(
                'Cannot define constant "%s". That name is already taken.'
                % const_spec.name
            )
        self.const_specs[const_spec.name] = const_spec

    def add_surface(self, name, surface):
        assert surface is not None

        if hasattr(self.module, name):
            raise ThriftCompilerError(
                'Cannot define "%s". The name has already been used.' % name
            )

        setattr(self.module, name, surface)

    def add_function(self, name, func):
        """Adds a top-level function with the given name to the module.

        :param name:
            Name of the function.
        :param func:
            Function to add to the module.
        """
        assert func is not None

        if hasattr(self.module, name):
            raise ThriftCompilerError(
                'Cannot define "%s". The name has already been used.' % name
            )

        setattr(self.module, name, func)

    def add_type_spec(self, name, spec, lineno):
        """Adds the given type to the scope.

        :param str name:
            Name of the new type
        :param spec:
            ``TypeSpec`` object containing information on the type, or a
            ``TypeReference`` if this is meant to be resolved during the
            ``link`` stage.
        :param lineno:
            Line number on which this type is defined.
        """
        assert type is not None

        if name in self.type_specs:
            raise ThriftCompilerError(
                'Cannot define type "%s" at line %d. '
                'Another type with that name already exists.'
                % (name, lineno)
            )

        self.type_specs[name] = spec

    def add_include_scope(self, scope):
        """"""

        assert scope is not None

        scope_name = scope.module.__name__

        if hasattr(self.module, scope_name):
            raise ThriftCompilerError(
                'Cannot define include "%s". The name has already been used.' % scope_name
            )

        if scope_name in self.include_scopes:
            raise ThriftCompilerError(
                'Cannot define include "%s". That name is already taken.'
                % scope_name
            )

        self.include_scopes[scope_name] = scope
        setattr(self.module, scope_name, scope.module)
