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

import os.path

from .idl import Parser
from .compile import Compiler
from .protocol import BinaryProtocol


class Loader(object):
    """Loads and compiles Thrift files."""

    __slots__ = ('parser', 'compiler')

    def __init__(self, protocol=None):
        """Initialize a loader.

        :param thriftrw.protocol.Protocol protocol:
            The protocol to use to serialize and deserialize types. Defaults
            to the binary protocol.
        """
        protocol = BinaryProtocol()

        self.parser = Parser()
        self.compiler = Compiler(protocol)

    def loads(self, name, document):
        """Parse and compile the given Thrift document.

        :param str name:
            Name of the Thrift document.
        :param str document:
            The Thrift IDL as a string.
        """
        program = self.parser.parse(document)
        return self.compiler.compile(name, program)

    def load(self, path, name=None):
        """Load and compile the given Thrift file.

        :param str path:
            Path to the ``.thrift`` file.
        :param str name:
            Name of the generated module. Defaults to the base name of the
            ``.thrift`` file.
        """
        # TODO do we care if the file extension is .thrift?
        if name is None:
            name = os.path.splitext(os.path.basename(path))[0]
        with open(path, 'r') as f:
            document = f.read()
        return self.loads(name, document)


_DEFAULT_LOADER = Loader()

#: Parses and compiles the given Thrift file.
#:
#: Uses the binary protocol to serialize and deserialize values.
#:
#: For more advanced use, see :py:class:`thriftrw.loader.Loader`.
load = _DEFAULT_LOADER.load


__all__ = ['Loader', 'load']
