"""
This module defines classes that provide an intermediate representation for
types going over-the-wire.

A set of wrapper classes is defined that contain just enough information going
to or from the wire. Custom types that can be sent over Thrift need to only
define a mapping to/from these ``*Value`` classes.
"""
from __future__ import absolute_import, unicode_literals, print_function

import abc

from collections import namedtuple

from .types import TType

# TODO: This module should mostly be cython.


class Value(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def apply(self, visitor):
        """Apply the value to the given visitor.

        The appropriate `visit_*` method will be called and its result
        returned.
        """
        pass


class BoolValue(namedtuple('BoolValue', 'value'), Value):
    """Wrapper for boolean values."""
    TTYPE = TType.BOOL

    def apply(self, visitor):
        return visitor.visit_bool(self.value)

    def __nonzero__(self):
        # in case someone tests truthiness on this
        return self.value

    __bool__ = __nonzero__  # Python 3


class ByteValue(namedtuple('ByteValue', 'value'), Value):
    """Wrapper for byte values."""
    TTYPE = TType.BYTE

    def apply(self, visitor):
        return visitor.visit_byte(self.value)


class DoubleValue(namedtuple('DoubleValue', 'value'), Value):
    """Wrapper for double values."""
    TTYPE = TType.DOUBLE

    def apply(self, visitor):
        return visitor.visit_double(self.value)


class I16Value(namedtuple('I16Value', 'value'), Value):
    """Wrapper for 16-bit integer values."""
    TTYPE = TType.I16

    def apply(self, visitor):
        return visitor.visit_i16(self.value)


class I32Value(namedtuple('I32Value', 'value'), Value):
    """Wrapper for 32-bit integer values."""
    TTYPE = TType.I32

    def apply(self, visitor):
        return visitor.visit_i32(self.value)


class I64Value(namedtuple('I64Value', 'value'), Value):
    """Wrapper for 64-bit integer values."""
    TTYPE = TType.I64

    def apply(self, visitor):
        return visitor.visit_i64(self.value)


class BinaryValue(namedtuple('BinaryValue', 'value'), Value):
    """Wrapper for binary blobs.

    Note that Thrift does not differentiate between text and binary blobs over
    the wire. UTF-8 text should be encoded/decoded manually.
    """
    TTYPE = TType.BINARY

    def apply(self, visitor):
        return visitor.visit_binary(self.value)


class StructField(namedtuple('StructField', 'id ttype value'), Value):
    """A single field in a struct.

    ``id``
        Field identifier of the struct.
    ``ttype``
        Type of value held by the struct. This must be a value from TType.
    ``value``
        Value held by the struct.
    """


class StructValue(namedtuple('StructValue', 'fields'), Value):
    """A struct value is a collection of fields of different types.

    ``fields``
        Collection of :py:class:`StructField` objects.
    """
    TTYPE = TType.STRUCT

    def __new__(cls, fields):
        if not isinstance(fields, dict):
            fields = {(field.id, field.ttype): field for field in fields}

        return super(StructValue, cls).__new__(cls, fields)

    def apply(self, visitor):
        return visitor.visit_struct(self.fields.values())

    def get(self, field_id, field_ttype):
        """Returns the value at the given field ID and type.

        :param field_id:
            Numerical field identifier.
        :param field_ttype:
            Type of the value.
        :returns:
            Value stored for the given field ID and type, or None if a field
            with the given ID and type was not found.
        """
        return self.fields.get((field_id, field_ttype))


class MapValue(namedtuple('MapValue', 'key_ttype value_ttype pairs'), Value):
    """A mapping of two different kinds of values.

    This object may be treated as a map.

    ``key_ttype``
        Type of the keys stored in the map. This must be a value from TType.
    ``value_ttype``
        Type of the values stored in the map. This must be a value from TType.
    ``pairs``
        Collection of key-value tuples. Note that this is **not** a dict.
    """
    TTYPE = TType.MAP

    def apply(self, visitor):
        return visitor.visit_map(self.key_ttype, self.value_ttype, self.pairs)


class SetValue(namedtuple('SetValue', 'value_ttype values'), Value):
    """A collection of unique values of the same type.

    ``value_ttype``
        Type of values in the set. This must be a value from TType.
    ``values``
        Collection of the values.
    """
    TTYPE = TType.SET

    def apply(self, visitor):
        return visitor.visit_set(self.value_ttype, self.values)


class ListValue(namedtuple('ListValue', 'value_ttype values'), Value):
    """A collection of values.

    ``value_ttype``
        Type of values in the list. This must be a value from TType.
    ``values``
        Collection of the values.
    """
    TTYPE = TType.LIST

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

        :param value:
            True or False
        """
        pass

    @abc.abstractmethod
    def visit_byte(self, value):
        """Visits 8-bit integers."""
        pass

    @abc.abstractmethod
    def visit_double(self, value):
        """Visits double values."""
        pass

    @abc.abstractmethod
    def visit_i16(self, value):
        """Visits 16-bit integers."""
        pass

    @abc.abstractmethod
    def visit_i32(self, value):
        """Visits 32-bit integers."""
        pass

    @abc.abstractmethod
    def visit_i64(self, value):
        """Visits 64-bit integers."""
        pass

    @abc.abstractmethod
    def visit_binary(self, value):
        """Visits binary blobs."""
        pass

    @abc.abstractmethod
    def visit_struct(self, fields):
        """Visits structs.

        :param fields:
            Collection of :py:class:`StructField` objects.
        """
        pass

    @abc.abstractmethod
    def visit_map(self, key_ttype, value_ttype, pairs):
        """Visits maps.

        :param key_ttype:
            Integer representing type of keys in the map.
        :param value_ttype:
            Integer representing type of values in the map.
        :param pairs:
            Collection of key-value pairs.
        """
        pass

    @abc.abstractmethod
    def visit_set(self, value_ttype, values):
        """Visits sets.

        :param value_ttype:
            Integer representing type of values in the set.
        :param values:
            Collection of values in the set.
        """
        pass

    @abc.abstractmethod
    def visit_list(self, value_ttype, values):
        """Visits lists.

        :param value_ttype:
            Integer representing type of values in the list.
        :param values:
            Collection of values in the list.
        """
        pass
