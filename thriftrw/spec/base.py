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

import abc

__all__ = ['TypeSpec']


class TypeSpec(object):
    """Base class for classes representing TypeSpecs.

    A TypeSpec knows how to convert values of the corresponding type to and
    from the intermediate Thrift representation (as defined in
    ``thriftrw.wire.value``).
    """
    __metaclass__ = abc.ABCMeta

    @property
    def name(self):
        """Name of the type referenced by this type spec."""
        raise NotImplementedError

    @property
    def ttype_code(self):
        """Numeric TType used for the type spec.

        The value must be from ``thriftrw.wire.TType``.
        """
        raise NotImplementedError

    @property
    def surface(self):
        """The surface of a type spec.

        The surface of a type spec, if non-None is the value associated with
        its name at the top-level in the generated module.
        """
        return None

    @abc.abstractmethod
    def to_wire(self, value):
        """Converts the given value into a :py:class:`Value` object."""
        pass

    @abc.abstractmethod
    def from_wire(self, wire_value):
        """Converts the given `Value` back into the original type.

        :param thriftr.wire.Value wire_value:
            Value to convert."""
        pass  # TODO define some way of failing the conversion

    @abc.abstractmethod
    def link(self, scope):
        """Link any types this type depends on.

        This may mutate this type.

        :returns:
            The linked type, or self.
        """
