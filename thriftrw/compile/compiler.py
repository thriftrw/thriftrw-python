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

from .gather import Gatherer
from .link import Linker
from .scope import Scope
from .const import ConstValueResolver
from .exceptions import ThriftCompilerError


class Compiler(object):

    def __init__(self, protocol):
        self.scope = Scope()
        self.values = ConstValueResolver(self.scope)

        self.protocol = protocol

    def compile(self, name, program):
        # NOTE we're ignoring name for now but we can use it later to
        # namespace definitions when we do support includes.

        # TODO the class responsible for the code generation pass should know
        # about the moodule and the name

        for header in program.headers:
            header.apply(self)

        gatherer = Gatherer(self.scope)
        for definition in program.definitions:
            gatherer.gather(definition)

        # TODO Linker can probably just be a callable.
        Linker(self.scope).link()

        # TODO return final module. for now, return scope to help debugging
        return self.scope

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
