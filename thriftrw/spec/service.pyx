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

from collections import namedtuple

from thriftrw.wire.value cimport Value
from thriftrw.protocol.core cimport ProtocolReader, FieldHeader
from .field cimport FieldSpec
from .union cimport UnionTypeSpec
from .struct cimport StructTypeSpec
from . cimport check

from .spec_mapper import type_spec_or_ref
from ..errors import ThriftCompilerError
from ..errors import UnknownExceptionError

__all__ = [
    'ServiceSpec',
    'FunctionSpec',
    'ServiceFunction',
    'FunctionArgsSpec',
    'FunctionResultSpec',
]


cdef class FunctionArgsSpec(StructTypeSpec):
    """Represents the parameters of a service function.

    .. py:attribute:: function

        The :py:class:`FunctionSpec` whose arguments this spec represents.
        This value is available only after the spec has been linked.

    The parameters of a function implicitly form a struct which contains the
    parameters as its fields, which are optional by default.

    The surface for this is the same as :py:class:`StructTypeSpec` except that
    the generated class also includes the following class attributes.

    .. py:attribute:: result_type

        A reference to the class representing the result type for
        ``function``, or None if the function was oneway.

    .. versionchanged:: 1.0

        Added the ``function`` attribute.

    .. versionchanged:: 1.1

        Added ``result_type`` class attribute to the surface.
    """

    def __init__(self, name, params):
        super(FunctionArgsSpec, self).__init__(name, params)
        self.function = None

    @classmethod
    def compile(cls, parameters, service_name, function_name):
        """Compiles a parameter list into a FunctionArgsSpec.

        :param parameters:
            Collection of :py:class:`thriftrw.idl.Field` objects.
        :param str service_name:
            Name of the service under which the function was defined.
        :param str function_name:
            Name of the function whose parameter list is represented by this
            object.
        """
        args_name = str('%s_%s_request' % (service_name, function_name))
        param_specs = [
            FieldSpec.compile(
                field=param,
                struct_name=args_name,
                require_requiredness=False,
            ) for param in parameters
        ]

        return cls(args_name, param_specs)

    def link(self, scope, function):
        self.function = function
        spec = super(FunctionArgsSpec, self).link(scope)

        result_type = None
        if self.function.result_spec is not None:
            result_spec = self.function.result_spec.link(scope, function)
            result_type = result_spec.surface

        spec.surface.result_type = result_type
        return spec


cdef class FunctionResultSpec(UnionTypeSpec):
    """Represents the result of a service function.

    .. py:attribute:: return_spec

        :py:class:`thriftrw.spec.TypeSpec` of the return type or None if the
        function does not return anything.

    .. py:attribute:: exception_specs

        Collection of :py:class:`thriftrw.spec.FieldSpec` objects defining the
        exceptions that this function can raise.

    .. py:attribute:: function

        The :py:class:`FunctionSpec` whose result type this spec represents.
        This value is available only after the spec has been linked.

    The return value of a function and the exceptions raised by it implicitly
    form a union which contains the return value at field ID ``0`` and the
    exceptions on the remaining field IDs.

    .. versionchanged:: 0.2

        Expose the class and add the ``return_spec`` and ``exception_specs``
        attributes.

    .. versionchanged:: 0.5

        When deserializing, if an unrecognized exception is found, a
        :py:class:`thriftrw.errors.UnknownExceptionError` is raised.

    .. versionchanged:: 1.0

        Added the ``function`` attribute.
    """

    def __init__(self, name, return_spec, exceptions):
        self.return_spec = return_spec
        self.exception_specs = exceptions
        self.function = None

        result_specs = []
        if return_spec is not None:
            result_specs.append(
                FieldSpec(
                    id=0,
                    name='success',
                    spec=return_spec,
                    required=False,
                    default_value=None
                )
            )

        result_specs.extend(exceptions)

        # Set of field IDs for exceptions recognized by this result. If the
        # system tries to read a field with an unrecognized exception ID, an
        # ``UnknownExceptionError`` will be raised.
        self.exception_ids = frozenset([f.id for f in exceptions])

        super(FunctionResultSpec, self).__init__(
            name, result_specs, allow_empty=(return_spec is None)
        )

    cpdef object read_from(FunctionResultSpec self, ProtocolReader reader):
        reader.read_struct_begin()

        cdef dict kwargs = {}
        cdef object val
        cdef FieldSpec spec
        cdef FieldHeader header

        header = reader.read_field_begin()

        # We use -1 to signify struct end due to cython constraints.
        while header.type != -1:
            spec = self._index.get((header.id, header.type), None)

            if spec is None:
                if header.id != 0:
                    raise UnknownExceptionError(
                        (
                            '"%s" received an unrecognized exception. '
                            'Make sure your Thrift IDL is up-to-date with '
                            'what the remote host is using.'
                        ) % self.name,
                    )
                else:
                    reader.skip(header.type)
            else:
                val = spec.spec.read_from(reader)
                kwargs[spec.name] = val

            reader.read_field_end()
            header = reader.read_field_begin()

        reader.read_struct_end()

        return self.surface(**kwargs)

    cpdef object from_wire(self, Value wire_value):
        check.type_code_matches(self, wire_value)

        for field in wire_value.fields:
            if field.id != 0 and field.id not in self.exception_ids:
                raise UnknownExceptionError(
                    (
                        '"%s" received an unrecognized exception. '
                        'Make sure your Thrift IDL is up-to-date with '
                        'what the remote host is using.'
                    ) % self.name,
                    wire_value,
                )

        return super(FunctionResultSpec, self).from_wire(wire_value)

    def link(self, scope, function):
        self.function = function
        if self.return_spec is not None:
            self.return_spec = self.return_spec.link(scope)
        self.exception_specs = [e.link(scope) for e in self.exception_specs]
        return super(FunctionResultSpec, self).link(scope)

    @classmethod
    def compile(cls, return_type, exceptions, service_name, function_name):
        """Compiles information from the AST into a FunctionResultSpec.

        :param return_type:
            A :py:class:`thriftrw.idl.Type` representing the return type or
            None if the function doesn't return anything.
        :param exceptions:
            Collection of :py:class:`thriftrw.idl.Field` objects representing
            raised by the function.
        :param str service_name:
            Name of the service under which the function was defined.
        :param str function_name:
            Name of the function whose result this object represents.
        """
        exceptions = exceptions or []
        result_name = str('%s_%s_response' % (service_name, function_name))

        if return_type is not None:
            return_spec = type_spec_or_ref(return_type)
        else:
            return_spec = None

        exc_specs = []
        for exc in exceptions:
            exc_specs.append(
                FieldSpec.compile(
                    field=exc,
                    struct_name=result_name,
                    require_requiredness=False,
                )
            )

        return cls(result_name, return_spec, exc_specs)


cdef class FunctionSpec(object):
    """Specification of a single function on a service.

    .. py:attribute:: name

        Name of the function.

    .. py:attribute:: service

        The :py:class:`ServiceSpec` that contains this function.
        This value is available only after the spec has been linked.

        .. versionadded:: 1.1

    .. py:attribute:: args_spec

        :py:class:`FunctionArgsSpec` specifying the arguments accepted by this
        function as a struct.

    .. py:attribute:: result_spec

        :py:class:`FunctionResultSpec` specifying the output of this
        function as a  union of the return type and the exceptions raised
        by this function.

        The return type of the function (if any) is a field in the union
        with field ID 0 and name 'success'.

        This value is None if the function is oneway.

    .. py:attribute:: oneway

        Whether this function is oneway or not.

    The ``surface`` for a FunctionSpec is a :py:class:`ServiceFunction`
    object. Unlike the ``surface`` for other specs, a FunctionSpec's surface
    is attached to the service class as a class attribute.

    .. versionchanged:: 0.3

        Added the ``oneway`` attribute.
    """

    def __init__(self, name, args_spec, result_spec, oneway):
        self.name = str(name)
        self.args_spec = args_spec
        self.result_spec = result_spec
        self.oneway = oneway
        self.linked = False
        self.surface = None
        self.service = None

    @classmethod
    def compile(cls, func, service_name):
        args_spec = FunctionArgsSpec.compile(
            parameters=func.parameters,
            service_name=service_name,
            function_name=func.name,
        )

        if func.oneway:
            result_spec = None
            if func.return_type is not None:
                raise ThriftCompilerError(
                    'Function "%s.%s" is oneway. It cannot return a value.'
                    % (service_name, func.name)
                )
            if func.exceptions:
                raise ThriftCompilerError(
                    'Function "%s.%s" is oneway. It cannot raise exceptions.'
                    % (service_name, func.name)
                )
        else:
            result_spec = FunctionResultSpec.compile(
                return_type=func.return_type,
                exceptions=func.exceptions,
                service_name=service_name,
                function_name=func.name,
            )

        return cls(func.name, args_spec, result_spec, func.oneway)

    cpdef FunctionSpec link(self, scope, ServiceSpec service):
        if not self.linked:
            self.service = service
            self.linked = True
            if self.result_spec:
                self.result_spec = self.result_spec.link(scope, self)
                result_spec_surface = self.result_spec.surface
            else:
                result_spec_surface = None
            self.args_spec = self.args_spec.link(scope, self)

            self.surface = ServiceFunction(
                self.name,
                self.args_spec.surface,
                result_spec_surface,
                self,
            )
        return self

    def __str__(self):
        return 'FunctionSpec(name=%r, args_spec=%r, result_spec=%r)' % (
            self.name, self.args_spec, self.result_spec
        )

    def __repr__(self):
        return str(self)


cdef class ServiceSpec(object):
    """Spec for a single service.

    .. py:attribute:: name

        Name of the service.

    .. py:attribute:: functions

        Collection of :py:class:`FunctionSpec` objects.

    .. py:attribute:: parent

        ``ServiceSpec`` of the parent service or None if this service does not
        inherit any service.

    The ``surface`` for a ``ServiceSpec`` is a class that has the following
    attributes:

    .. py:attribute:: service_spec

        :py:class:`ServiceSpec` for this service.

    And a reference to one :py:class:`ServiceFunction` object for each
    function defined in the service.
    """

    def __init__(self, name, functions, parent):
        self.name = str(name)
        self.functions = functions
        self.parent = parent

        # For quick function lookups.
        self._functions = None
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
            names.add(func.name)
            functions.append(
                FunctionSpec.compile(func, service.name)
            )

        return cls(service.name, functions, service.parent)

    cpdef ServiceSpec link(self, scope):
        if not self.linked:
            self.linked = True

            if self.parent is not None:
                self.parent = scope.resolve_service_spec(
                    self.parent.name, self.parent.lineno
                )

            self.functions = [func.link(scope, self) for func in self.functions]
            self.surface = service_cls(self, scope)

            # Build index for lookup. Normalize type of names to bytes since
            # it may be bytes or unicode.
            self._functions = {}
            for f in self.functions:
                name = f.name
                if isinstance(name, unicode):
                    name = name.encode('utf-8')
                self._functions[name] = f

        return self

    def lookup(self, name):
        """Look up a function with the given name.

        Returns the function spec or None if no such function exists.

        .. versionadded:: 1.0
        """
        if isinstance(name, unicode):
            name = name.encode('utf-8')
        return self._functions.get(name, None)

    def __str__(self):
        return 'ServiceSpec(name=%r, functions=%r, parent=%r)' % (
            self.name, self.functions, self.parent
        )

    def __repr__(self):
        return str(self)


class ServiceFunction(
    namedtuple('ServiceFunction', 'name request response spec')
):
    """Represents a single function on a service.

    .. py:attribute:: name

        Name of the function.

    .. py:attribute:: request

        Class representing requests for this function.

    .. py:attribute:: response

        Class representing responses for this function, or ``None`` if this
        function is ``oneway``.

    .. py:attribute:: spec

        :py:class:`thriftrw.spec.FunctionSpec` for this function.

    .. versionchanged:: 0.3

        Added the ``spec`` attribute.
    """


def service_cls(service_spec, scope):
    """Generates a class from the given service spec.

    :param ServiceSpec service_spec:
        Specification of the service.
    :param scope:
        Compilation scope.
    """
    parent_cls = object
    if service_spec.parent is not None:
        parent_cls = service_spec.parent.surface

    service_dct = {}
    for function in service_spec.functions:
        service_dct[function.name] = function.surface

    service_dct['service_spec'] = service_spec
    service_dct['__slots__'] = ()

    return type(str(service_spec.name), (parent_cls,), service_dct)
