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
    from :py:class:`thriftrw.wire.Value` objects.
    """
    __metaclass__ = abc.ABCMeta

    @property
    def name(self):
        """Name of the type referenced by this type spec."""
        raise NotImplementedError

    @property
    def ttype_code(self):
        """Numeric TType used for the type spec.

        The value must be from :py:data:`thriftrw.wire.TType`.
        """
        raise NotImplementedError

    @property
    def surface(self):
        """The surface of a type spec.

        The surface of a type spec, if non-None is the value associated with
        its name at the top-level in the generated module.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def to_wire(self, value):
        """Converts the given value into a :py:class:`thriftrw.wire.Value`
        object.

        :returns thriftrw.wire.Value:
            Wire representation of the value.
        :raises TypeError:
            If the value did not match the type expected by this TypeSpec.
        :raises ValueError:
            If the value matched the type but did not hold the correct set of
            acceptable values.
        """

    @abc.abstractmethod
    def from_wire(self, wire_value):
        """Converts the given :py:class:`thriftrw.wire.Value` back into the
        original type.

        :param thriftr.wire.Value wire_value:
            Value to convert.
        :raises ValueError:
            If the type of the wire value does not have the correct Thrift
            type for this type spec.
        """

    @abc.abstractmethod
    def link(self, scope):
        pass
