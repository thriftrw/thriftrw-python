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
from collections import deque
from collections import namedtuple

import thriftrw.wire.value as V
from thriftrw.wire import TType

from .exceptions import ThriftCompilerError


class Type(object):
    """Base class for classes representing Types.

    A Type knows how to convert values of the corresponding type to and from
    the intermediate Thrift representation (as defined in
    ``thriftrw.wire.value``).
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def to_wire(self, value):
        """Converts the given value into a :py:class:`Value` object."""
        pass

    @abc.abstractmethod
    def from_wire(self, wire_value):
        """Converts the given :py:class:`Value` back into the original type.
        """
        pass  # TODO define some way of failing the conversion

    @abc.abstractproperty
    def ttype_code(self):
        """Get the numeric TType identifier for this type."""
        pass

    def link(self, scope):
        """Given the final scope object, links to types this type depends on.

        Returns self.
        """
        return self

    @property
    def is_reference(self):
        """Returns True if the given object is a reference to another type.

        All concrete Types must return False for this.
        """
        return False


class TypeReference(namedtuple('TypeReference', 'name lineno')):
    """A reference to another type."""

    @property
    def is_reference(self):
        return True

    def link(self, scope):
        """Resolves and returns the referenced type."""

        typ = self
        visited = set([])
        while typ.is_reference:

            if typ.name in visited:
                raise ThriftCompilerError(
                    'Type "%s" at line %d is a reference to itself.'
                    % (self.name, self.lineno)
                )

            if typ.name not in scope.types:
                raise ThriftCompilerError(
                    'Unknown type "%s" referenced at line %d'
                    % (typ.name, typ.lineno)
                )

            visited.add(typ.name)
            typ = scope.types[typ.name]

        # Connect all visited references to this type.
        result = typ
        for t in visited:
            scope.types[t] = result

        return result


class PrimitiveType(Type, namedtuple('PrimitiveType', 'code value_cls')):

    @property
    def ttype_code(self):
        return self.code

    def to_wire(self, value):
        return self.value_cls(value)

    def from_wire(self, wire_value):
        # TODO validate types?
        return wire_value.value


class _TextType(Type):

    __slots__ = ()

    @property
    def ttype_code(self):
        return TType.BINARY

    def to_wire(self, value):
        return V.BinaryValue(value.encode('utf-8'))

    def from_wire(self, wire_value):
        return wire_value.value.decode('utf-8')


BoolType = PrimitiveType(TType.BOOL, V.BoolValue)
ByteType = PrimitiveType(TType.BYTE, V.ByteValue)
DoubleType = PrimitiveType(TType.DOUBLE, V.DoubleValue)
I16Type = PrimitiveType(TType.I16, V.I16Value)
I32Type = PrimitiveType(TType.I32, V.I32Value)
I64Type = PrimitiveType(TType.I64, V.I64Value)
BinaryType = PrimitiveType(TType.BINARY, V.BinaryValue)
TextType = _TextType()


class Field(object):
    """A single field on a struct.

    :param int id:
        Field ID
    :param str name:
        Name of the attribute on the class it's attached with.
    :param Type ftype:
        :py:class:`Type` object containing information about the kind of value
        this field can store.
    """

    __slots__ = ('id', 'name', 'ftype')

    def __init__(self, id, name, ftype):
        self.id = id
        self.name = name
        self.ftype = ftype

    def link(self, scope):
        self.ftype = self.ftype.link(scope)
        return self

    def __str__(self):
        return 'Field(id=%r, name=%r, ftype=%r)' % (
            self.id, self.name, self.ftype
        )

    __repr__ = __str__


class StructType(Type, namedtuple('StructType', 'cls fields')):
    """A struct is a collection of named fields.

    :param cls:
        Class or constructor of the native type. It must accept all defined
        fields as named args.
    :param fields:
        Collection of :py:class:`Field` objects.
    """

    @property
    def ttype_code(self):
        return TType.STRUCT

    def to_wire(self, value):
        fields = deque()

        for field in self.fields:
            field_value = getattr(value, field.name, None)
            if field_value is None:
                continue

            field_value = field.ftype.to_wire(field_value)
            fields.append(
                V.FieldValue(
                    id=field.id,
                    ttype=field.ftype.ttype_code,
                    value=field_value,
                )
            )

        return V.StructValue(fields)

    def from_wire(self, wire_value):
        kwargs = {}
        for field in self.fields:
            ftype = field.ftype
            value = wire_value.get(field.id, ftype.ttype_code)
            if value is not None:
                kwargs[field.name] = ftype.from_wire(value)

        # TODO For the case where cls fails to instantiate because a required
        # positional argument is missing, we know that the request was
        # invalid.
        return self.cls(**kwargs)

    def link(self, scope):
        for field in self.fields:
            field.link(scope)
        return self


class MapType(Type):
    """
    :param Type ktype:
        Type of the keys in the map.
    :param Type vtype:
        Type of the values in the map.
    """

    __slots__ = ('ktype', 'vtype')

    def __init__(self, ktype, vtype):
        self.ktype = ktype
        self.vtype = vtype

    @property
    def ttype_code(self):
        return TType.MAP

    def to_wire(self, value):
        return V.MapValue(
            key_ttype=self.ktype.ttype_code,
            value_ttype=self.vtype.ttype_code,
            pairs=[
                (self.ktype.to_wire(k), self.vtype.to_wire(v))
                for k, v in value.items()
            ]
        )

    def from_wire(self, wire_value):
        return {
            self.ktype.from_wire(k): self.vtype.from_wire(v)
            for k, v in wire_value.pairs
        }

    def link(self, scope):
        self.ktype = self.ktype.link(scope)
        self.vtype = self.vtype.link(scope)
        return self

    def __str__(self):
        return 'MapType(ktype=%r, vtype=%r)' % (self.ktype, self.vtype)

    __repr__ = __str__


class SetType(Type):
    """
    :param Type vtype:
        Type of values stored in the set.
    """

    __slots__ = ('vtype',)

    def __init__(self, vtype):
        self.vtype = vtype

    @property
    def ttype_code(self):
        return TType.SET

    def to_wire(self, value):
        return V.SetValue(
            value_ttype=self.vtype.ttype_code,
            values=[self.vtype.to_wire(v) for v in value],
        )

    def from_wire(self, wire_value):
        return set(
            self.vtype.from_wire(v) for v in wire_value.values
        )

    def link(self, scope):
        self.vtype = self.vtype.link(scope)
        return self

    def __str__(self):
        return 'SetType(vtype=%r)' % self.vtype

    __repr__ = __str__


class ListType(Type):
    """
    :param Type vtype:
        Type of values stored in the list.
    """

    __slots__ = ('vtype',)

    def __init__(self, vtype):
        self.vtype = vtype

    @property
    def ttype_code(self):
        return TType.LIST

    def to_wire(self, value):
        return V.ListValue(
            value_ttype=self.vtype.ttype_code,
            values=[self.vtype.to_wire(v) for v in value],
        )

    def from_wire(self, wire_value):
        return [self.vtype.from_wire(v) for v in wire_value.values]

    def link(self, scope):
        self.vtype = self.vtype.link(scope)
        return self

    def __str__(self):
        return 'ListType(vtype=%r)' % self.vtype

    __repr__ = __str__
