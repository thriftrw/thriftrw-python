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

from collections import namedtuple

from .ttype import TType

# TODO: This module should mostly be cython.

__all__ = [
    'Value',
    'BoolValue',
    'ByteValue',
    'DoubleValue',
    'I16Value',
    'I32Value',
    'I64Value',
    'BinaryValue',
    'FieldValue',
    'StructValue',
    'MapValue',
    'SetValue',
    'ListValue',
    'ValueVisitor',
]


class Value(object):
    """Base class for Value classes.

    Value classes define an intermediate representation of Thrift types as
    they are sent and received over the wire.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def apply(self, visitor):
        """Apply the value to the given visitor.

        The appropriate `visit_*` method will be called and its result
        returned.

        :param ValueVisitor visitor:
            Visitor on the value.
        :returns:
            Value returned by the corresponding ``visit_*`` method.
        """
        pass


class BoolValue(namedtuple('BoolValue', 'value'), Value):
    """Wrapper for boolean values."""

    ttype_code = TType.BOOL

    def apply(self, visitor):
        return visitor.visit_bool(self.value)


class ByteValue(namedtuple('ByteValue', 'value'), Value):
    """Wrapper for byte values."""

    ttype_code = TType.BYTE

    def apply(self, visitor):
        return visitor.visit_byte(self.value)


class DoubleValue(namedtuple('DoubleValue', 'value'), Value):
    """Wrapper for double values."""

    ttype_code = TType.DOUBLE

    def apply(self, visitor):
        return visitor.visit_double(self.value)


class I16Value(namedtuple('I16Value', 'value'), Value):
    """Wrapper for 16-bit integer values."""

    ttype_code = TType.I16

    def apply(self, visitor):
        return visitor.visit_i16(self.value)


class I32Value(namedtuple('I32Value', 'value'), Value):
    """Wrapper for 32-bit integer values."""

    ttype_code = TType.I32

    def apply(self, visitor):
        return visitor.visit_i32(self.value)


class I64Value(namedtuple('I64Value', 'value'), Value):
    """Wrapper for 64-bit integer values."""

    ttype_code = TType.I64

    def apply(self, visitor):
        return visitor.visit_i64(self.value)


class BinaryValue(namedtuple('BinaryValue', 'value'), Value):
    """Wrapper for binary blobs.

    Note that Thrift does not differentiate between text and binary blobs over
    the wire. UTF-8 text should be encoded/decoded manually.
    """

    ttype_code = TType.BINARY

    def apply(self, visitor):
        return visitor.visit_binary(self.value)


class FieldValue(namedtuple('FieldValue', 'id ttype value'), Value):
    """A single field in a struct.

    .. py:attribute:: id

        Field identifier.

    .. py:attribute:: ttype

        :py:data:`~thriftrw.wire.TType` of the value held in this field.

    .. py:attribute:: value

        Value for this field.
    """


class StructValue(Value):
    """A struct value is a collection of fields of different types.

    .. py:attribute:: fields

        Collection of :py:class:`FieldValue` objects.
    """

    ttype_code = TType.STRUCT

    __slots__ = ('fields', '_index')

    def __init__(self, fields):
        self.fields = fields

        self._index = {}
        for field in fields:
            self._index[(field.id, field.ttype)] = field

    def apply(self, visitor):
        return visitor.visit_struct(self.fields)

    def get(self, field_id, field_ttype):
        """Returns the value at the given field ID and type.

        :param field_id:
            Numerical field identifier.
        :param field_ttype:
            Type of the value.
        :returns:
            Corresponding ``FieldValue`` or None.
        """
        field_value = self._index.get((field_id, field_ttype))
        if field_value is None:
            return None
        else:
            return field_value

    def __str__(self):
        return 'StructValue(%r)' % self.fields

    __repr__ = __str__

    def __eq__(self, other):
        return self.fields == other.fields


class MapValue(namedtuple('MapValue', 'key_ttype value_ttype pairs'), Value):
    """A mapping of two different kinds of values.

    This object may be treated as a map.

    .. py:attribute:: key_ttype

        Type of the keys stored in the map. This must be a value from TType.

    .. py:attribute:: value_ttype

        Type of the values stored in the map. This must be a value from TType.

    .. py:attribute:: pairs

        Collection of key-value tuples. Note that this is **not** a dict.
    """

    ttype_code = TType.MAP

    def apply(self, visitor):
        return visitor.visit_map(self.key_ttype, self.value_ttype, self.pairs)


class SetValue(namedtuple('SetValue', 'value_ttype values'), Value):
    """A collection of unique values of the same type.

    .. py:attribute:: value_ttype

        Type of values in the set. This must be a value from TType.

    .. py:attribute:: values

        Collection of the values.
    """

    ttype_code = TType.SET

    def apply(self, visitor):
        return visitor.visit_set(self.value_ttype, self.values)


class ListValue(namedtuple('ListValue', 'value_ttype values'), Value):
    """A collection of values.

    .. py:attribute:: value_ttype

        Type of values in the list. This must be a value from TType.

    .. py:attribute:: values

        Collection of the values.
    """

    ttype_code = TType.LIST

    def apply(self, visitor):
        return visitor.visit_list(self.value_ttype, self.values)


class ValueVisitor(object):
    """Visitor on different value types.

    The ``visit_*`` functions are not given the ``*Value`` objects but the
    actual values contained in them.

    The idea is that when something needs to take an arbitrary Thrift value
    and act on all cases, it extends this type. Each Thrift value knows which
    function to call on the visitor based on the value type. The intention
    here is to avoid ``isinstance`` checks.
    """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def visit_bool(self, value):
        """Visits boolean values.

        :param bool value:
            True or False
        """
        pass

    @abc.abstractmethod
    def visit_byte(self, value):
        """Visits 8-bit integers.

        :param int value:
            8-bit integer
        """
        pass

    @abc.abstractmethod
    def visit_double(self, value):
        """Visits double values.

        :param float value:
            Floating point number
        """
        pass

    @abc.abstractmethod
    def visit_i16(self, value):
        """Visits 16-bit integers.

        :param int value:
            16-bit integer
        """
        pass

    @abc.abstractmethod
    def visit_i32(self, value):
        """Visits 32-bit integers.

        :param int value:
            32-bit integer
        """
        pass

    @abc.abstractmethod
    def visit_i64(self, value):
        """Visits 64-bit integers.

        :param int value:
            64-bit integer
        """
        pass

    @abc.abstractmethod
    def visit_binary(self, value):
        """Visits binary blobs.

        :param bytes value:
            Binary blob
        """
        pass

    @abc.abstractmethod
    def visit_struct(self, fields):
        """Visits structs.

        :param fields:
            Collection of :py:class:`FieldValue` objects.
        """
        pass

    @abc.abstractmethod
    def visit_map(self, key_ttype, value_ttype, pairs):
        """Visits maps.

        :param thriftrw.wire.TType key_ttype:
            TType of the keys in the map.
        :param thriftrw.wire.TType value_ttype:
            TType of the values in the map.
        :param pairs:
            Collection of key-value pairs.
        """
        pass

    @abc.abstractmethod
    def visit_set(self, value_ttype, values):
        """Visits sets.

        :param thriftrw.wire.TType value_ttype:
            TType of the items in the set.
        :param values:
            Collection of values in the set.
        """
        pass

    @abc.abstractmethod
    def visit_list(self, value_ttype, values):
        """Visits lists.

        :param thriftrw.wire.TType value_ttype:
            TType of the items in the set.
        :param values:
            Collection of values in the list.
        """
        pass
