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

from .spec_mapper import type_spec_or_ref


class TypedefTypeSpec(object):
    """Typedefs are aliases for other types.

    Typedefs resolve themselves to the target type at link time and eliminate
    themselves from the tree.
    """

    __slots__ = ('name', 'target_spec')

    def __init__(self, name, target_spec):
        self.name = name
        self.target_spec = target_spec

    @classmethod
    def compile(cls, typedef):
        target_spec = type_spec_or_ref(typedef.target_type)
        return cls(typedef.name, target_spec)

    def link(self, scope):
        return self.target_spec.link(scope)

    def __str__(self):
        return 'TypedefTypeSpec(%r, %r)' % (self.name, self.target_spec)

    __repr__ = __str__

    def __eq__(self, other):
        return (
            self.name == other.name and
            self.target_spec == other.target_spec
        )
