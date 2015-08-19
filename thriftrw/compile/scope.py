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

from .exceptions import ThriftCompilerError

__all__ = ['Scope']


class Scope(object):
    """Maintains the compilation state across steps.

    The scope is not exported to the user directly. It's only used to maintain
    state of known types and values during the compilation process and holds a
    reference to the final generated module.
    """

    __slots__ = ('const_values', 'type_specs', 'module', 'service_specs')

    def __init__(self, name):
        """Initialize the scope.

        :param name:
            Name of the generated module.
        """
        self.const_values = {}
        self.type_specs = {}
        self.service_specs = {}

        self.module = types.ModuleType(name)

    def __str__(self):
        return "Scope(%r)" % {
            'const_values': self.const_values,
            'type_specs': self.type_specs,
            'service_specs': self.service_specs,
            'module': self.module,
        }

    __repr__ = __str__

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

    def add_constant(self, name, value, lineno):
        """Registers the given constant into the scope.

        :param name:
            Name of the constant.
        :param value:
            Value of the contsant.
        :param lineno:
            The line number at which this constant was defined.
        :raises ThriftCompilerError:
            If the constant name has already been used.
        """
        assert value is not None

        if name in self.const_values or hasattr(self.module, name):
            raise ThriftCompilerError(
                'Cannot define constant "%s" at line %d. '
                'That name is already taken.'
                % (name, lineno)
            )

        self.const_values[name] = value
        setattr(self.module, name, value)

    def add_class(self, cls):
        """Adds a class to the generated module.

        :param cls:
            Class to add to the generatde module.
        :raises ThriftCompilerError:
            If the name of the class has already been used.
        """
        assert cls is not None

        name = cls.__name__
        if hasattr(self.module, name):
            raise ThriftCompilerError(
                'Cannot define "%s". The name has already been used.' % name
            )

        setattr(self.module, name, cls)

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
