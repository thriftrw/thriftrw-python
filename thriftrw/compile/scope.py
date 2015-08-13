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

from .exceptions import ThriftCompilerError


class Scope(object):
    """Represents the compilation scope.

    The scope is not exported to the user directly. It's only used to maintain
    state of known types and values during the compilation process.
    """

    __slots__ = ('const_values', 'type_specs', 'services')

    def __init__(self):
        self.const_values = {}
        self.type_specs = {}
        self.services = {}

    def __str__(self):
        return "Scope(const_values=%r, type_specs=%r, services=%r)" % (
            self.const_values, self.type_specs, self.services
        )

    __repr__ = __str__

    def add_constant(self, name, value, lineno):
        assert value is not None

        if name in self.const_values:
            raise ThriftCompilerError(
                'Cannot define constant "%s" at line %d. '
                'That name is already taken.'
                % (name, lineno)
            )

        self.const_values[name] = value

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

        # TODO link constant types and value references.
        # TODO it would be preferable if scope did not have any business
        # logic.
