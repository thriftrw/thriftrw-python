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

import types

from ..errors import ThriftCompilerError

__all__ = ['Scope']


class Scope(object):
    """Maintains the compilation state across steps.

    The scope is not exported to the user directly. It's only used to maintain
    state of known types and values during the compilation process and holds a
    reference to the final generated module.
    """

    __slots__ = (
        'const_specs', 'type_specs', 'module', 'service_specs',
        'included_scopes', 'path'
    )

    def __init__(self, name, path=None):
        """Initialize the scope.

        :param name:
            Name of the generated module.
        """
        self.path = path
        self.type_specs = {}
        self.const_specs = {}
        self.service_specs = {}
        self.included_scopes = {}

        self.module = types.ModuleType(str(name))

    def __str__(self):
        return "Scope(%r)" % {
            'const_specs': self.const_specs,
            'type_specs': self.type_specs,
            'service_specs': self.service_specs,
            'module': self.module,
        }

    __repr__ = __str__

    def __in_path(self):
        """Helper for error messages to say "in $path" if the scope has a
        non-none path.
        """
        if self.path:
            return ' in "%s"' % self.path
        else:
            return ''

    def resolve_const_spec(self, name, lineno):
        """Finds and links the ConstSpec with the given name."""

        if name in self.const_specs:
            return self.const_specs[name].link(self)

        if '.' in name:
            include_name, component = name.split('.', 1)
            if include_name in self.included_scopes:
                return self.included_scopes[include_name].resolve_const_spec(
                    component, lineno
                )

        raise ThriftCompilerError(
            'Unknown constant "%s" referenced at line %d%s' % (
                name, lineno, self.__in_path()
            )
        )

    def resolve_type_spec(self, name, lineno):
        """Finds and links the TypeSpec with the given name."""

        if name in self.type_specs:
            return self.type_specs[name].link(self)

        if '.' in name:
            include_name, component = name.split('.', 1)
            if include_name in self.included_scopes:
                return self.included_scopes[include_name].resolve_type_spec(
                    component, lineno
                )

        raise ThriftCompilerError(
            'Unknown type "%s" referenced at line %d%s' % (
                name, lineno, self.__in_path()
            )
        )

    def resolve_service_spec(self, name, lineno):
        """Finds and links the ServiceSpec with the given name."""

        if name in self.service_specs:
            return self.service_specs[name].link(self)

        if '.' in name:
            include_name, component = name.split('.', 2)
            if include_name in self.included_scopes:
                return self.included_scopes[
                    include_name
                ].resolve_service_spec(component, lineno)

        raise ThriftCompilerError(
            'Unknown service "%s" referenced at line %d%s' % (
                name, lineno, self.__in_path()
            )
        )

    def add_include(self, name, included_scope, module):
        """Register an imported module into this scope.

        Raises ``ThriftCompilerError`` if the name has already been used.
        """
        # The compiler already ensures this. If we still get here with a
        # conflict, that's a bug.
        assert name not in self.included_scopes

        self.included_scopes[name] = included_scope
        self.add_surface(name, module)

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
        """Adds a top-level attribute with the given name to the module."""
        assert surface is not None

        if hasattr(self.module, name):
            raise ThriftCompilerError(
                'Cannot define "%s". The name has already been used.' % name
            )

        setattr(self.module, name, surface)

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
