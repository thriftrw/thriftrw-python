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

from collections import deque


from .exceptions import ThriftCompilerError


class Linker(object):
    """Links together type references."""

    __slots__ = ('scope',)

    def __init__(self, scope):
        self.scope = scope

    def link(self):
        """Resolve and link all types in the scope."""

        # collection of types whose subtypes need to be linked.
        to_link = deque()

        # Resolve top level type references.
        for name in self.scope.types.keys():
            typ = self.resolve_type(self.scope.types[name])
            self.scope.types[name] = typ
            to_link.append(typ)

        visited = set()

        def typ_link(typ):
            typ = self.resolve_type(typ)
            if typ not in visited:
                # Ask for this type's subtypes to be linked
                to_link.append(typ)
            return typ

        while to_link:
            typ = to_link.popleft()
            if typ in visited:
                # Already linked.
                continue
            visited.append(typ)
            typ.transform_types(typ_link)

    def resolve_type(self, typ):
        """Resolves a TypeReference to a Type.

        Does not resolve or link any subtypes."""

        visited = set()
        while typ.is_reference:

            if typ.name in visited:
                raise ThriftCompilerError(
                    'Type "%s" at line %d is a reference to itself.'
                    % (self.name, self.lineno)
                )

            if typ.name not in self.scope.types:
                raise ThriftCompilerError(
                    'Unknown type "%s" referenced at line %d'
                    % (typ.name, typ.lineno)
                )

            visited.add(typ.name)
            typ = self.scope.types[typ.name]

        return typ
