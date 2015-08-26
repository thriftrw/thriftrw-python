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

from thriftrw.compile.exceptions import ThriftCompilerError

from .spec_mapper import type_spec_or_ref
from .struct import StructTypeSpec, FieldSpec
from .union import UnionTypeSpec


__all__ = ['ServiceSpec', 'FunctionSpec']


class FunctionArgsSpec(StructTypeSpec):

    @classmethod
    def compile(cls, parameters, service_name, function_name):
        args_name = str('%s_%s_request' % (service_name, function_name))
        param_specs = [
            FieldSpec.compile(
                field=param,
                struct_name=args_name,
                require_requiredness=False,
            ) for param in parameters
        ]

        return cls(args_name, param_specs)


class FunctionResultSpec(UnionTypeSpec):

    @classmethod
    def compile(cls, return_type, exceptions, service_name, function_name):
        result_name = str('%s_%s_response' % (service_name, function_name))

        result_specs = []
        if return_type is not None:
            result_specs.append(
                FieldSpec(
                    id=0,
                    name='success',
                    spec=type_spec_or_ref(return_type),
                    required=False,
                    default_value=None
                )
            )

        for exc in exceptions:
            result_specs.append(
                FieldSpec.compile(
                    field=exc,
                    struct_name=result_name,
                    require_requiredness=False,
                )
            )

        return cls(result_name, result_specs)


class FunctionSpec(object):

    __slots__ = ('name', 'args_spec', 'result_spec', 'linked', 'surface')

    def __init__(self, name, args_spec, result_spec):
        self.name = name
        self.args_spec = args_spec
        self.result_spec = result_spec
        self.linked = False
        self.surface = None

    @classmethod
    def compile(cls, func, service_name):
        if func.oneway:
            raise ThriftCompilerError(
                'Function "%s.%s" is oneway. '
                'Oneway functions are not supported by thriftrw.'
                % (service_name, func.name)
            )

        args_spec = FunctionArgsSpec.compile(
            parameters=func.parameters,
            service_name=service_name,
            function_name=func.name,
        )

        result_spec = FunctionResultSpec.compile(
            return_type=func.return_type,
            exceptions=func.exceptions,
            service_name=service_name,
            function_name=func.name,
        )

        return cls(func.name, args_spec, result_spec)

    def link(self, scope):
        if not self.linked:
            self.linked = True
            self.args_spec = self.args_spec.link(scope)
            self.result_spec = self.result_spec.link(scope)
            self.surface = ServiceFunction(
                self.name,
                self.args_spec.surface,
                self.result_spec.surface,
            )
        return self

    def __str__(self):
        return 'FunctionSpec(name=%r, args_spec=%r, result_spec=%r)' % (
            self.name, self.args_spec, self.result_spec
        )

    __repr__ = __str__


class ServiceSpec(object):

    __slots__ = ('name', 'functions', 'parent', 'linked', 'surface')

    def __init__(self, name, functions, parent):
        self.name = name
        self.functions = functions
        self.parent = parent
        self.linked = False
        self.surface = None

    @classmethod
    def compile(cls, service):
        functions = []
        names = set()

        for func in service.functions:
            if func.name in names:
                raise ThriftCompilerError(
                    'Function "%s.%s" cannot be defined. '
                    'That name is already taken.'
                    % (service.name, func.name)
                )
            functions.append(
                FunctionSpec.compile(func, service.name)
            )

        return cls(service.name, functions, service.parent)

    def link(self, scope):
        if not self.linked:
            self.linked = True

            if self.parent is not None:
                if self.parent not in scope.service_specs:
                    raise ThriftCompilerError(
                        'Service "%s" inherits from unknown service "%s"'
                        % (self.name, self.parent)
                    )
                self.parent = scope.service_specs[self.parent].link(scope)

            self.functions = [func.link(scope) for func in self.functions]
            self.surface = service_cls(self, scope)

        return self

    def __str__(self):
        return 'ServiceSpec(name=%r, functions=%r, parent=%r)' % (
            self.name, self.functions, self.parent
        )

    __repr__ = __str__


class ServiceFunction(namedtuple('ServiceFunction', 'name request response')):
    """Represents a single function on a service.

    ``name``
        Name of the function.
    ``request``
        Class representing requests for this function.
    ``response``
        Class representing responses for this function.
    """


def service_cls(service_spec, scope):
    parent_cls = object
    if service_spec.parent is not None:
        parent_cls = service_spec.parent.surface

    service_dct = {}
    for function in service_spec.functions:
        service_dct[function.name] = function.surface

    service_dct['service_spec'] = service_spec
    service_dct['__slots__'] = ()

    return type(str(service_spec.name), (parent_cls,), service_dct)
