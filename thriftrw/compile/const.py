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


class ConstValueResolver(object):
    """Resolves constant values."""

    __slots__ = ('scope',)

    def __init__(self, scope):
        """
        :param Scope scope:
            Scope which will be queried for constants.
        """
        self.scope = scope

    def resolve(self, const_value):
        """Resolve the given constant value.

        :param const_value:
            A ``thriftrw.idl.ConstValue``
        :returns:
            The value that the ``ConstValue`` maps to.
        """
        return const_value.apply(self)

    def visit_primitive(self, const):
        return const.value

    def visit_reference(self, const):
        value = self.scope.constants.get(const.name)
        if value is None:
            raise ThriftCompilerError(
                'Unknown constant "%s" referenced at line %d'
                % (const.name, const.lineno)
            )
        return value

    # NOTE We do not yet support forward references in constants.
