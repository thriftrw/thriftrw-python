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


__all__ = ['TypeSpecLinker', 'ServiceSpecLinker']


class TypeSpecLinker(object):
    """Links together references in TypeSpecs."""

    __slots__ = ('scope',)

    def __init__(self, scope):
        self.scope = scope

    def link(self):
        """Resolve and link all types in the scope."""

        type_specs = {}
        types = []

        for name, type_spec in self.scope.type_specs.items():
            type_spec = type_spec.link(self.scope)
            type_specs[name] = type_spec

            if type_spec.surface is not None:
                self.scope.add_surface(name, type_spec.surface)
                types.append(type_spec.surface)

        self.scope.type_specs = type_specs
        self.scope.add_surface('types', tuple(types))


class ServiceSpecLinker(object):
    """Links references to type in service specs."""

    __slots__ = ('scope',)

    def __init__(self, scope):
        self.scope = scope

    def link(self):
        service_specs = {}
        services = []

        for name, service_spec in self.scope.service_specs.items():
            service_spec = service_spec.link(self.scope)
            service_specs[name] = service_spec

            if service_spec.surface is not None:
                self.scope.add_surface(
                    service_spec.name, service_spec.surface
                )
                services.append(service_spec.surface)

        self.scope.service_specs = service_specs
        self.scope.add_surface('services', tuple(services))


class ConstSpecLinker(object):
    """Links references to top-level constants."""

    __slots__ = ('scope',)

    def __init__(self, scope):
        self.scope = scope

    def link(self):
        const_specs = {}
        constants = {}

        for name, const_spec in self.scope.const_specs.items():
            const_spec = const_spec.link(self.scope)
            const_specs[name] = const_spec

            if const_spec.surface is not None and const_spec.save:
                self.scope.add_surface(
                    const_spec.name, const_spec.surface
                )
                constants[const_spec.name] = const_spec.surface

        self.scope.const_specs = const_specs
        self.scope.add_surface('constants', constants)
