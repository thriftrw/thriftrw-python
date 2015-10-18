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

from libc.stdint cimport (
    int8_t,
    int16_t,
    int32_t,
    int64_t,
)

from .ttype import TType

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


cdef bint richcompare_op(int op, int compare):
    # op    operation
    # 0     <
    # 1     <=
    # 2     ==
    # 3     !=
    # 4     >
    # 5     >=

    if op == 2:
        return compare == 0
    elif op == 3:
        return compare != 0
    elif op == 4:
        return compare > 0
    elif op == 5:
        return compare >= 0
    elif op == 0:
        return compare < 0
    elif op == 1:
        return compare <= 0
    else:
        assert False, 'Invalid comparison operator "%d"' % (op,)


cdef bint richcompare(int op, list pairs):
    """Utility function to make ``richcmp`` easier to write.

    It takes a list of attribute pairs. Attributes are compared in the order
    they appear and the result is returned based on the ``op``.

    .. code-block:: python

        def __richcmp__(self, other, op):
            return richcompare(
                op,
                [
                    (self.attr1, other.attr1),
                    (self.attr2, other.attr2),
                    # ...
                ]
            )
    """

    cdef int compare = 0

    for (left, right) in pairs:
        if left > right:
            compare = 1
            break
        elif left < right:
            compare = -1
            break

    return richcompare_op(op, compare)


cdef class Value:
    """Base class for Value classes.

    Value classes define an intermediate representation of Thrift types as
    they are sent and received over the wire.
    """

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


cdef class BoolValue(Value):
    """Wrapper for boolean values."""

    ttype_code = TType.BOOL

    def __cinit__(self, bint value):
        self.value = value

    def __richcmp__(BoolValue self, BoolValue other not None, int op):
        return richcompare(op, [(self.value, other.value)])

    def __str__(self):
        return 'BoolValue(%r)' % (self.value,)

    def __repr__(self):
        return str(self)

    def apply(self, visitor):
        return visitor.visit_bool(self.value)


cdef class ByteValue(Value):
    """Wrapper for byte values."""

    ttype_code = TType.BYTE

    def __cinit__(self, int8_t value):
        self.value = value

    def __richcmp__(ByteValue self, ByteValue other not None, int op):
        return richcompare(op, [(self.value, other.value)])

    def __str__(self):
        return 'ByteValue(%r)' % (self.value,)

    def __repr__(self):
        return str(self)

    def apply(self, visitor):
        return visitor.visit_byte(self.value)


cdef class DoubleValue(Value):
    """Wrapper for double values."""

    ttype_code = TType.DOUBLE

    def __cinit__(self, double value):
        self.value = value

    def __richcmp__(DoubleValue self, DoubleValue other not None, int op):
        return richcompare(op, [(self.value, other.value)])

    def __str__(self):
        return 'DoubleValue(%r)' % (self.value,)

    def __repr__(self):
        return str(self)

    def apply(self, visitor):
        return visitor.visit_double(self.value)


cdef class I16Value(Value):
    """Wrapper for 16-bit integer values."""

    ttype_code = TType.I16

    def __cinit__(self, int16_t value):
        self.value = value

    def __richcmp__(I16Value self, I16Value other not None, int op):
        return richcompare(op, [(self.value, other.value)])

    def __str__(self):
        return 'I16Value(%r)' % (self.value,)

    def __repr__(self):
        return str(self)

    def apply(self, visitor):
        return visitor.visit_i16(self.value)


cdef class I32Value(Value):
    """Wrapper for 32-bit integer values."""

    ttype_code = TType.I32

    def __cinit__(self, int value):
        self.value = value

    def __richcmp__(I32Value self, I32Value other not None, int op):
        return richcompare(op, [(self.value, other.value)])

    def __str__(self):
        return 'I32Value(%r)' % (self.value,)

    def __repr__(self):
        return str(self)

    def apply(self, visitor):
        return visitor.visit_i32(self.value)


cdef class I64Value(Value):
    """Wrapper for 64-bit integer values."""

    ttype_code = TType.I64

    def __cinit__(self, long value):
        self.value = value

    def __richcmp__(I64Value self, I64Value other not None, int op):
        return richcompare(op, [(self.value, other.value)])

    def __str__(self):
        return 'I64Value(%r)' % (self.value,)

    def __repr__(self):
        return str(self)

    def apply(self, visitor):
        return visitor.visit_i64(self.value)


cdef class BinaryValue(Value):
    """Wrapper for binary blobs.

    Note that Thrift does not differentiate between text and binary blobs over
    the wire. UTF-8 text should be encoded/decoded manually.
    """

    ttype_code = TType.BINARY

    def __cinit__(self, bytes value):
        self._value = value
        self.value = value

    def __richcmp__(BinaryValue self, BinaryValue other not None, int op):
        return richcompare(op, [(self.value, other.value)])

    def __str__(self):
        return 'BinaryValue(%r)' % (self.value,)

    def __repr__(self):
        return str(self)

    def apply(self, visitor):
        return visitor.visit_binary(self.value)


cdef class FieldValue(object):
    """A single field in a struct.

    .. py:attribute:: id

        Field identifier.

    .. py:attribute:: ttype

        :py:data:`~thriftrw.wire.TType` of the value held in this field.

    .. py:attribute:: value

        Value for this field.
    """

    def __cinit__(self, int16_t id, int8_t ttype, Value value):
        self.id = id
        self.ttype = ttype
        self.value = value

    def __str__(self):
        return 'FieldValue(%r, %r, %r)' % (self.id, self.ttype, self.value)

    def __repr__(self):
        return str(self)

    def __richcmp__(FieldValue self, FieldValue other not None, int op):
        return richcompare(op, [
            (self.id, other.id),
            (self.ttype, other.ttype),
            (self.value, other.value),
        ])


cdef class StructValue(Value):
    """A struct value is a collection of fields of different types.

    .. py:attribute:: fields

        Collection of :py:class:`FieldValue` objects.
    """

    ttype_code = TType.STRUCT

    def __cinit__(self, list fields):
        self.fields = fields

    def __init__(self, list fields):
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

    def __richcmp__(StructValue self, StructValue other not None, int op):
        return richcompare(op, [(self.fields, other.fields)])

    def __str__(self):
        return 'StructValue(%r)' % self.fields

    def __repr__(self):
        return str(self)


cdef class MapItem(object):
    """An item in a map.

    .. py:attribute:: key

        Key of the item

    .. py:attribute:: value

        Value associated with the key
    """

    def __cinit__(self, Value key, Value value):
        self.key = key
        self.value = value

    def __str__(self):
        return 'MapValue(%r, %r)' % (self.key, self.value)

    def __repr__(self):
        return str(self)

    def __richcmp__(MapItem self, MapItem other not None, int op):
        return richcompare(op, [
            (self.key, other.key),
            (self.value, other.value),
        ])


cdef class MapValue(Value):
    """A mapping of two different kinds of values.

    This object may be treated as a map.

    .. py:attribute:: key_ttype

        Type of the keys stored in the map. This must be a value from TType.

    .. py:attribute:: value_ttype

        Type of the values stored in the map. This must be a value from TType.

    .. py:attribute:: pairs

        Collection of :py:class:`MapItem` objects.
    """

    ttype_code = TType.MAP

    def __cinit__(self, int8_t key_ttype, int8_t value_ttype, list pairs):
        self.key_ttype = key_ttype
        self.value_ttype = value_ttype
        self.pairs = pairs

    def __richcmp__(MapValue self, MapValue other not None, int op):
        return richcompare(op, [
            (self.key_ttype, other.key_ttype),
            (self.value_ttype, other.value_ttype),
            (self.pairs, other.pairs),
        ])

    def __str__(self):
        return 'MapValue(%r)' % (self.pairs,)

    def __repr__(self):
        return str(self)

    def apply(self, visitor):
        return visitor.visit_map(self.key_ttype, self.value_ttype, self.pairs)


cdef class SetValue(Value):
    """A collection of unique values of the same type.

    .. py:attribute:: value_ttype

        Type of values in the set. This must be a value from TType.

    .. py:attribute:: values

        Collection of the values.
    """

    ttype_code = TType.SET

    def __cinit__(self, int8_t value_ttype, list values):
        self.value_ttype = value_ttype
        self.values = values

    def __str__(self):
        return 'SetValue(%r)' % (self.values,)

    def __repr__(self):
        return str(self)

    def __richcmp__(SetValue self, SetValue other not None, int op):
        return richcompare(op, [
            (self.value_ttype, other.value_ttype),
            (self.values, other.values),
        ])

    def apply(self, visitor):
        return visitor.visit_set(self.value_ttype, self.values)


cdef class ListValue(Value):
    """A collection of values.

    .. py:attribute:: value_ttype

        Type of values in the list. This must be a value from TType.

    .. py:attribute:: values

        Collection of the values.
    """

    ttype_code = TType.LIST

    def __cinit__(self, int8_t value_ttype, list values):
        self.value_ttype = value_ttype
        self.values = values

    def __str__(self):
        return 'ListValue(%r)' % (self.values,)

    def __repr__(self):
        return str(self)

    def __richcmp__(ListValue self, ListValue other not None, int op):
        return richcompare(op, [
            (self.value_ttype, other.value_ttype),
            (self.values, other.values),
        ])

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

    def visit_bool(self, value):
        """Visits boolean values.

        :param bool value:
            True or False
        """
        pass

    def visit_byte(self, value):
        """Visits 8-bit integers.

        :param int value:
            8-bit integer
        """
        pass

    def visit_double(self, value):
        """Visits double values.

        :param float value:
            Floating point number
        """
        pass

    def visit_i16(self, value):
        """Visits 16-bit integers.

        :param int value:
            16-bit integer
        """
        pass

    def visit_i32(self, value):
        """Visits 32-bit integers.

        :param int value:
            32-bit integer
        """
        pass

    def visit_i64(self, value):
        """Visits 64-bit integers.

        :param int value:
            64-bit integer
        """
        pass

    def visit_binary(self, value):
        """Visits binary blobs.

        :param bytes value:
            Binary blob
        """
        pass

    def visit_struct(self, fields):
        """Visits structs.

        :param fields:
            Collection of :py:class:`FieldValue` objects.
        """
        pass

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

    def visit_set(self, value_ttype, values):
        """Visits sets.

        :param thriftrw.wire.TType value_ttype:
            TType of the items in the set.
        :param values:
            Collection of values in the set.
        """
        pass

    def visit_list(self, value_ttype, values):
        """Visits lists.

        :param thriftrw.wire.TType value_ttype:
            TType of the items in the set.
        :param values:
            Collection of values in the list.
        """
        pass
