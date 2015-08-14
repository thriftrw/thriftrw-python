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

from collections import namedtuple

from .exceptions import ThriftCompilerError


class ServiceFunction(namedtuple('ServiceFunction', 'name request response')):
    """Represents a single function on a service.

    ``name``
        Name of the function.
    ``request``
        Class representing requests for this function.
    ``response``
        Class representing responses for this function.
    """

    def __call__(self, *args, **kwargs):
        return self.request(*args, **kwargs)


class ServiceCompiler(object):

    def __init__(self, scope):
        self.scope = scope
        self.compiled = {}

    def compile(self):
        for name in self.scope.service_specs.keys():
            self.compile_service(name)

    def compile_service(self, name, visited=None):
        if name in self.compiled:
            return self.compiled

        visited = set() if visited is None else visited

        if name not in self.scope.service_specs:
            raise ThriftCompilerError('Unknown service "%s".' % name)

        if name in visited:
            raise ThriftCompilerError(
                'Service "%s" inherits itself or a service that inherits it. '
                'Cyclic inheritance between services is not supported.'
                % name
            )

        visited.add(name)

        service_spec = self.scope.service_specs[name]
        base_cls = object
        service_dct = {}

        if service_spec.parent is not None:
            # Recursively resolve service dependencies.
            base_cls = self.compile_service(service_spec.parent, visited)

        service_dct = {}
        service_functions = []
        for func_spec in service_spec.functions:
            if func_spec.name in service_dct:
                raise ThriftCompilerError(
                    'Function "%s.%s" cannot be defined. '
                    'That name is already taken.'
                    % (service_spec.name, func_spec.name)
                )

            args_cls = func_spec.args_spec.cls
            result_cls = func_spec.result_spec.cls

            function = ServiceFunction(func_spec.name, args_cls, result_cls)
            service_functions.append(function)
            service_dct[func_spec.name] = function

        service_functions = tuple(service_functions)
        if service_spec.parent is not None:
            service_functions = base_cls.service_functions + service_functions

        service_dct['service_functions'] = service_functions
        service_dct['__slots__'] = ()

        service_cls = type(service_spec.name, (base_cls,), service_dct)
        self.compiled[service_spec.name] = service_cls
        self.scope.add_class(service_cls)

        return service_cls
