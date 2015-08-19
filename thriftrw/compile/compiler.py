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

from .generate import Generator
from .link import TypeSpecLinker
from .link import ServiceSpecLinker
from .scope import Scope
from .exceptions import ThriftCompilerError
from .service import ServiceCompiler


__all__ = ['Compiler']


class Compiler(object):
    """Compiles IDLs into Python modules."""

    LINKERS = [TypeSpecLinker, ServiceSpecLinker]

    def __init__(self, protocol):
        """Initialize the compiler.

        :param thriftrw.protocol.Protocol protocol:
           The protocol ot use to serialize and deserialize values.
        """
        self.protocol = protocol

    def compile(self, name, program):
        """Compile the given parsed Thrift document.

        :param str name:
            Name of the Thrift document. This will be the name of the
            generated module.
        :param thriftrw.idl.Program program:
            AST of the parsted Thrift document.
        """
        scope = Scope(name)

        for header in program.headers:
            header.apply(self)

        generator = Generator(scope)
        for definition in program.definitions:
            generator.process(definition)

        # TODO Linker can probably just be a callable.
        for linker in self.LINKERS:
            linker(scope).link()

        ServiceCompiler(scope).compile()
        # TODO add load and dump methods to module
        return scope.module

    def visit_include(self, include):
        raise ThriftCompilerError(
            'Include of "%s" found on line %d. '
            'thriftrw does not support including other Thrift files.'
            % (include.path, include.lineno)
        )

    def visit_namespace(self, namespace):
        pass  # nothing to do


# Reserved identifiers
# TODO forbid declared items from using these names
RESERVED = frozenset((
    'BEGIN',
    'END',
    '__CLASS__',
    '__DIR__',
    '__FILE__',
    '__FUNCTION__',
    '__LINE__',
    '__METHOD__',
    '__NAMESPACE__',
    'abstract',
    'alias',
    'and',
    'args',
    'as',
    'async',
    'assert',
    'await',
    'begin',
    'break',
    'case',
    'catch',
    'class',
    'clone',
    'continue',
    'declare',
    'def',
    'default',
    'del',
    'delete',
    'do',
    'dynamic',
    'elif',
    'else',
    'elseif',
    'elsif',
    'end',
    'enddeclare',
    'endfor',
    'endforeach',
    'endif',
    'endswitch',
    'endwhile',
    'ensure',
    'except',
    'exec',
    'finally',
    'float',
    'for',
    'foreach',
    'function',
    'global',
    'goto',
    'if',
    'implements',
    'import',
    'in',
    'inline',
    'instanceof',
    'interface',
    'is',
    'lambda',
    'module',
    'native',
    'new',
    'next',
    'nil',
    'not',
    'or',
    'pass',
    'public',
    'print',
    'private',
    'protected',
    'public',
    'raise',
    'redo',
    'rescue',
    'retry',
    'register',
    'return',
    'self',
    'sizeof',
    'static',
    'super',
    'switch',
    'synchronized',
    'then',
    'this',
    'throw',
    'transient',
    'try',
    'undef',
    'union',
    'unless',
    'unsigned',
    'until',
    'use',
    'var',
    'virtual',
    'volatile',
    'when',
    'while',
    'with',
    'xor',
    'yield'
))
