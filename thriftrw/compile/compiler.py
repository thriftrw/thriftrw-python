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

import os.path

from .scope import Scope
from .generate import Generator
from .link import TypeSpecLinker
from .link import ConstSpecLinker
from .link import ServiceSpecLinker
from ..errors import ThriftCompilerError

from thriftrw.idl import Parser
from thriftrw._runtime import Serializer, Deserializer


__all__ = ['Compiler']

LINKERS = [ConstSpecLinker, TypeSpecLinker, ServiceSpecLinker]


class ModuleSpec(object):
    """Specification for a single module."""

    __slots__ = (
        'name',
        'path',
        'scope',
        'surface',
        'includes',
        'protocol',
        'linked',
        'thrift_source',
    )

    def __init__(self, name, protocol, path=None, thrift_source=None):
        """
        :param name:
            Name of the module.
        :param path:
            Path to the Thrift file from which this module was compiled. This
            may be omitted if the module was compiled from an inline string
            (using the ``loads()`` API, for example).
        :param thrift_source:
            If non-None, this is the source code of the Thrift file from which
            this module was generated.
        """

        self.name = name
        self.path = path
        self.protocol = protocol
        self.linked = False
        self.scope = Scope(name, path)
        self.surface = self.scope.module
        self.thrift_source = thrift_source

        # Mapping of names of inculded modules to their corresponding specs.
        self.includes = {}

        # TODO Scope can probably be eventually folded into this class.

    @property
    def can_include(self):
        """Whether this module is allowed to include other modules.

        This is allowed only if the module was compiled from a file since
        include paths are relative to the file in which they are mentioned.
        """
        return self.path is not None

    def add_include(self, name, module_spec):
        """Adds a module as an included module.

        :param name:
            Name under which the included module should be exposed in the
            current module.
        :param module_spec:
            ModuleSpec of the included module.
        """
        assert name, 'name is required'
        assert self.can_include

        if name in self.includes:
            raise ThriftCompilerError(
                'Cannot include module "%s" as "%s" in "%s". '
                'The name is already taken.'
                % (module_spec.name, name, self.path)
            )

        self.includes[name] = module_spec
        self.scope.add_include(name, module_spec.scope, module_spec.surface)

    def link(self):
        """Link all the types in this module and all included modules."""
        if self.linked:
            return self

        self.linked = True

        included_modules = []

        # Link includes
        for include in self.includes.values():
            included_modules.append(include.link().surface)

        self.scope.add_surface('__includes__', tuple(included_modules))
        self.scope.add_surface('__thrift_source__', self.thrift_source)

        # Link self
        for linker in LINKERS:
            linker(self.scope).link()

        self.scope.add_surface('loads', Deserializer(self.protocol))
        self.scope.add_surface('dumps', Serializer(self.protocol))

        return self


class Compiler(object):
    """Compiles IDLs into Python modules."""

    __slots__ = (
        'protocol', 'strict', 'parser', 'include_as', '_module_specs'
    )

    def __init__(self, protocol, strict=None, include_as=None):
        """Initialize the compiler.

        :param thriftrw.protocol.Protocol protocol:
           The protocol ot use to serialize and deserialize values.
        """
        if strict is None:
            strict = True
        if include_as is None:
            include_as = False
        self.protocol = protocol
        self.strict = strict
        self.include_as = include_as

        self.parser = Parser()

        # Mapping from absolute file path to ModuleSpec for all modules.
        self._module_specs = {}

    def compile(self, name, contents, path=None):
        """Compile the given Thrift document into a Python module.

        The generated module contains,

        .. py:attribute:: __services__

            A collection of generated classes for all services defined in the
            thrift file.

            .. versionchanged:: 1.0

                Renamed from ``services`` to ``__services__``.

        .. py:attribute:: __types__

            A collection of generated types for all types defined in the
            thrift file.

            .. versionchanged:: 1.0

                Renamed from ``types`` to ``__types__``.

        .. py:attribute:: __includes__

            A collection of modules included by this module.

            .. versionadded:: 1.0

        .. py:attribute:: __constants__

            A mapping of constant name to value for all constants defined in
            the thrift file.

            .. versionchanged:: 1.0

                Renamed from ``constants`` to ``__constants__``.

        .. py:attribute:: __thrift_source__

            Contents of the .thrift file from which this module was compiled.

            .. versionadded:: 1.1

        .. py:function:: dumps(obj)

            Serializes the given object using the protocol the compiler was
            instantiated with.

        .. py:function:: loads(cls, payload)

            Deserializes an object of type ``cls`` from ``payload`` using the
            protocol the compiler was instantiated with.

        .. py:function:: dumps.message(obj, seqid=0)

            Serializes the given request or response into a
            :py:class:`~thriftrw.wire.Message` using the protocol that the
            compiler was instantiated with.

            See :ref:`calling-apache-thrift`.

            .. versionadded:: 1.0

        .. py:function:: loads.message(service, payload)

            Deserializes a :py:class:`~thriftrw.wire.Message`  from
            ``payload`` using the protocol the compiler was instantiated with.
            A request or response of a method defined in the given service is
            parsed in the message body.

            See :ref:`calling-apache-thrift`.

            .. versionadded:: 1.0

        And one class each for every struct, union, exception, enum, and
        service defined in the IDL.

        Service classes have references to
        :py:class:`thriftrw.spec.ServiceFunction` objects for each method
        defined in the service.

        :param str name:
            Name of the Thrift document. This will be the name of the
            generated module.
        :param str contents:
            Thrift document to compile
        :param str path:
            Path to the Thrift file being compiled. If not specified, imports
            from within the Thrift file will be disallowed.
        :returns:
            ModuleSpec of the generated module.
        """
        assert name

        if path:
            path = os.path.abspath(path)
            if path in self._module_specs:
                return self._module_specs[path]

        module_spec = ModuleSpec(name, self.protocol, path, contents)
        if path:
            self._module_specs[path] = module_spec

        program = self.parser.parse(contents)

        header_processor = HeaderProcessor(self, module_spec, self.include_as)
        for header in program.headers:
            header.apply(header_processor)

        generator = Generator(module_spec.scope, strict=self.strict)
        for definition in program.definitions:
            generator.process(definition)

        return module_spec


class HeaderProcessor(object):
    """Processes headers found in the Thrift file."""

    __slots__ = ('compiler', 'module_spec', 'include_as')

    def __init__(self, compiler, module_spec, include_as):
        self.compiler = compiler
        self.module_spec = module_spec
        self.include_as = include_as

    def visit_include(self, include):

        if not self.module_spec.can_include:
            raise ThriftCompilerError(
                'Include of "%s" found on line %d. '
                'Includes are not supported when using the "loads()" API.'
                'Try loading the file using the "load()" API.'
                % (include.path, include.lineno)
            )

        if not any(include.path.startswith(p) for p in ('./', '../')):
            raise ThriftCompilerError(
                'Paths in include statements are relative to the directory '
                'containing the Thrift file. They must be in the form '
                '"./foo.thrift" or "../bar.thrift".  Instead, found "%s"'
                % (include.path)
            )

        # Includes are relative to directory of the Thrift file being
        # compiled.
        path = os.path.join(
            os.path.dirname(self.module_spec.path), include.path
        )

        if not os.path.isfile(path):
            raise ThriftCompilerError(
                'Cannot include "%s" on line %d in %s. '
                'The file "%s" does not exist.'
                % (include.path, include.lineno, self.module_spec.path, path)
            )

        # name is the name of the module. included_name is the name under
        # which it's exposed inside the current module.
        name = os.path.splitext(os.path.basename(include.path))[0]

        if include.name and not self.include_as:
            raise ThriftCompilerError(
                'Cannot include "%s" as "%s" on line %d. '
                'The "include-as" syntax is currently disabled. '
                'Enable it by instantiating a Loader with include_as=True'
                % (name, include.name, include.lineno)
            )

        included_name = include.name
        if included_name is None:
            included_name = name

        with open(path, 'r') as f:
            contents = f.read()

        included_module_spec = self.compiler.compile(name, contents, path)
        self.module_spec.add_include(included_name, included_module_spec)

    def visit_namespace(self, namespace):
        pass  # nothing to do
