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

from thriftrw.wire.value cimport Value
from thriftrw.protocol.core cimport ProtocolWriter, ProtocolReader

__all__ = ['TypeSpec']


cdef class TypeSpec:
    """Base class for classes representing TypeSpecs.

    A TypeSpec knows how to convert values of the corresponding type to and
    from :py:class:`thriftrw.wire.Value` objects.
    """
    __slots__ = ()

    property name:
        """Name of the type referenced by this type spec."""

        def __get__(self):
            raise NotImplementedError

    property surface:
        """The surface of a type spec.

        The surface of a type spec, if non-None is the value associated with
        its name at the top-level in the generated module.
        """

        def __get__(self):
            raise NotImplementedError

    cpdef object read_from(TypeSpec self, ProtocolReader reader):
        """Read a primitive value of this type from :py:class:`thriftrw.protocol.ProtocolReader`."""
        raise NotImplementedError

    cpdef void write_to(TypeSpec self, ProtocolWriter writer,
                        object value) except *:
        """Writes a value directly to :py:class:`thriftrw.protocol.ProtocolWriter`."""
        writer.write_value(self.to_wire(value))

    cpdef Value to_wire(TypeSpec self, object value):
        """Converts the given value into a :py:class:`thriftrw.wire.Value`
        object.

        :returns thriftrw.wire.Value:
            Wire representation of the value.
        """
        raise NotImplementedError(
            'to_wire called on unlinked type reference: %r', self
        )

    cpdef object from_wire(TypeSpec self, Value wire_value):
        """Converts the given :py:class:`thriftrw.wire.Value` back into the
        original type.

        :param thriftr.wire.Value wire_value:
            Value to convert.
        :raises ValueError:
            If the type of the wire value does not have the correct Thrift
            type for this type spec.
        """
        raise NotImplementedError(
            'from_wire called on unlinked type reference: %r', self
        )

    cpdef TypeSpec link(self, scope):
        raise NotImplementedError

    cpdef object to_primitive(TypeSpec self, object value):
        """Converts a value matching this type spec into a primitive value.

        A primitive value is a text, binary, integer, or float value, or a
        list or dict of other primitive values.

        .. versionadded:: 0.4

        :param value:
            Value matching this TypeSpec.
        :returns:
            A representation of that value using only primitive types, lists,
            and maps.
        """
        raise NotImplementedError(
            'to_primitive called on unlinked type reference: %r', self
        )

    cpdef object from_primitive(TypeSpec self, object prim_value):
        """Converts a primitive value into a value of this type.

        A primitive value is a text, binary, integer, or float value, or a
        list or dict of other primitive values.

        .. versionadded:: 0.4

        :param prim_value:
            A primitive value as produced by ``to_primitive``.
        :returns:
            A value matching this TypeSpec.
        """
        raise NotImplementedError(
            'from_primitive called on unlinked type reference: %r', self
        )

    cpdef void validate(TypeSpec self, object o) except *:
        """Whether an instance of this spec is valid.

        :param instance:
            An instance of the type described by this spec.

        :raises TypeError:
            If the value did not match the type expected by this TypeSpec.
        :raises ValueError:
            If the value matched the type but did not hold the correct set of
            acceptable values.
        """
        raise NotImplementedError(
            'validate called on unlinked type reference: %r', self
        )
