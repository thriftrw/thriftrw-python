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

import sys
import inspect
import os.path

from .idl import Parser
from .compile import Compiler
from .protocol import BinaryProtocol


class Loader(object):
    """Loads and compiles Thrift files."""

    __slots__ = ('parser', 'compiler', 'compiled_modules')

    def __init__(self, protocol=None):
        """Initialize a loader.

        :param thriftrw.protocol.Protocol protocol:
            The protocol to use to serialize and deserialize types. Defaults
            to the binary protocol.
        """
        protocol = BinaryProtocol()

        self.parser = Parser()
        self.compiler = Compiler(protocol)

        # Mapping of absolute file path to compiled module. This is used to
        # cache the result of calling load() multiple times on the same file.
        self.compiled_modules = {}

    def loads(self, name, document):
        """Parse and compile the given Thrift document.

        :param str name:
            Name of the Thrift document.
        :param str document:
            The Thrift IDL as a string.
        """
        program = self.parser.parse(document)
        return self.compiler.compile(name, program)

    def load(self, path, name=None, force=False):
        """Load and compile the given Thrift file.

        If the file was already compiled before, a cached copy of the compiled
        module is returned.

        :param str path:
            Path to the ``.thrift`` file.
        :param str name:
            Name of the generated module. Defaults to the base name of the
            file.
        :param bool force:
            Whether to ignore the cache and load the file anew. Defaults to
            False.
        :returns:
            The compiled module.
        """
        path = os.path.abspath(path)
        if path in self.compiled_modules and not force:
            return self.compiled_modules[path]

        if name is None:
            # TODO do we care if the file extension is .thrift?
            name = os.path.splitext(os.path.basename(path))[0]
        with open(path, 'r') as f:
            document = f.read()
        module = self.loads(name, document)
        self.compiled_modules[path] = module
        return module


_DEFAULT_LOADER = Loader()

#: Parses and compiles the given Thrift file.
#:
#: Uses the binary protocol to serialize and deserialize values.
#:
#: For more advanced use, see :py:class:`thriftrw.loader.Loader`.
#:
#: :param str path:
#:     Path to the ``.thrift`` file.
#: :param str name:
#:     Name of the generated module. Defaults to the basename of the file.
#: :param bool force:
#:     Whether to ignore the cache and load the file anew. Defaults to False.
#: :raises thriftrw.compile.ThriftCompilerError:
#:     If there was an error compiling the Thrift file.
load = _DEFAULT_LOADER.load


def install(path, name=None):
    """Compiles a Thrift file and installs it as a submodule of the caller.

    Given a tree organized like so::

        foo/
            __init__.py
            bar.py
            my_service.thrift

    You would do,

    .. code-block:: python

        my_service = thriftrw.install('my_service.thrift')

    To install ``my_service`` as a submodule of the module from which you made
    the call. If the call was made in ``foo/bar.py``, the compiled
    Thrift file will be installed as ``foo.bar.my_service``. If the call was
    made in ``foo/__init__.py``, the compiled Thrift file will be installed as
    ``foo.my_service``. This allows other modules to import ``from`` the
    compiled module like so,

    .. code-block:: python

        from foo.my_service import MyService

    .. versionadded:: 0.2

    :param path:
        Path of the Thrift file. This may be an absolute path, or a path
        relative to the Python module making the call.
    :param str name:
        Name of the submodule. Defaults to the basename of the Thrift file.
    :returns:
        The compiled module
    """
    if name is None:
        name = os.path.splitext(os.path.basename(path))[0]

    callermod = inspect.getmodule(inspect.stack()[1][0])
    name = '%s.%s' % (callermod.__name__, name)

    if name in sys.modules:
        return sys.modules[name]

    if not os.path.isabs(path):
        callerfile = callermod.__file__
        path = os.path.normpath(
            os.path.join(os.path.dirname(callerfile), path)
        )

    sys.modules[name] = mod = load(path, name=name)
    return mod


__all__ = ['Loader', 'load', 'install']
