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


class TypeSpec(object):
    """Base class for classes representing TypeSpecs.

    A TypeSpec knows how to convert values of the corresponding type to and
    from the intermediate Thrift representation (as defined in
    ``thriftrw.wire.value``).
    """
    __metaclass__ = abc.ABCMeta

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

    @abc.abstractproperty
    def ttype_code(self):
        """Get the numeric TType identifier for this type.
        
        :returns thriftrw.wire.TType:
            TType of the value represented by this spec.
        """
        pass

    def transform_dependencies(self, function):
        """Map the given function over dependencies of this type.

        Specs for types that depend on other types will execute this function
        on the specs for their direct dependencies and replace the dependency
        specifications with the values returned by the function. The
        implementations will NOT recursively call the function on dependencies
        of dependencies; that responsibility is with the caller.

        The default implementation for this does not do anything.

        :param function:
            A function that accepts accepts the current specification for a
            dependency and returns a possibly different specification.
        """

    @property
    def is_reference(self):
        """Returns True if the given object is a reference to another type.

        All concrete TypeSpecs must return False for this.
        """
        return False


class TypeReference(namedtuple('TypeReference', 'name lineno')):
    """A reference to another type."""

    @property
    def is_reference(self):
        return True

    # It may be worth making this implement the TypeSpec interface and raise
    # exceptions complaining about unresolved type references, since that's
    # probably a bug.


class PrimitiveTypeSpec(
    TypeSpec, namedtuple('PrimitiveTypeSpec', 'code value_cls')
):
    """TypeSpec for primitive types."""

    @property
    def ttype_code(self):
        return self.code

    def to_wire(self, value):
        return self.value_cls(value)

    def from_wire(self, wire_value):
        # TODO validate types?
        return wire_value.value


class _TextTypeSpec(TypeSpec):
    """TypeSpec for the text type."""

    __slots__ = ()

    @property
    def ttype_code(self):
        return TType.BINARY

    def to_wire(self, value):
        return V.BinaryValue(value.encode('utf-8'))

    def from_wire(self, wire_value):
        return wire_value.value.decode('utf-8')


#: TypeSpec for boolean values.
BoolTypeSpec = PrimitiveTypeSpec(TType.BOOL, V.BoolValue)

#: TypeSpec for single-byte integers.
ByteTypeSpec = PrimitiveTypeSpec(TType.BYTE, V.ByteValue)

#: TypeSpec for floating point numbers with 64 bits of precision.
DoubleTypeSpec = PrimitiveTypeSpec(TType.DOUBLE, V.DoubleValue)

#: TypeSpec for 16-bit integers.
I16TypeSpec = PrimitiveTypeSpec(TType.I16, V.I16Value)

#: TypeSpec for 32-bit integers.
I32TypeSpec = PrimitiveTypeSpec(TType.I32, V.I32Value)

#: TypeSpec for 64-bit integers.
I64TypeSpec = PrimitiveTypeSpec(TType.I64, V.I64Value)

#: TypeSpec for binary blobs.
BinaryTypeSpec = PrimitiveTypeSpec(TType.BINARY, V.BinaryValue)

#: TypeSpec for unicode data.
TextTypeSpec = _TextTypeSpec()


class FieldSpec(object):
    """Specification for a single field on a struct.

    :param int id:
        Field ID
    :param str name:
        Name of the attribute on the class it's attached with.
    :param TypeSpec spec:
        :py:class:`TypeSpec` object containing information about the kind of
        value this field can store.
    """

    __slots__ = ('id', 'name', 'spec')

    def __init__(self, id, name, spec):
        self.id = id
        self.name = name
        self.spec = spec

    def __str__(self):
        return 'FieldSpec(id=%r, name=%r, spec=%r)' % (
            self.id, self.name, self.spec
        )

    __repr__ = __str__

    # While FieldSpec has an interface similar to TypeSpec, it's not an actual
    # TypeSpec.

    def to_wire(self, value):
        assert value is not None
        return V.FieldValue(
            id=self.id,
            ttype=self.spec.ttype_code,
            value=self.spec.to_wire(value),
        )

    def from_wire(self, wire_value):
        assert wire_value is not None
        return self.spec.from_wire(wire_value.value)

    def transform_dependencies(self, function):
        self.spec = function(self.spec)


class StructTypeSpec(TypeSpec, namedtuple('StructTypeSpec', 'cls fields')):
    """A struct is a collection of named fields.

    :param cls:
        Class or constructor of the native type. It must accept all defined
        fields as named args.
    :param fields:
        Collection of :py:class:`FieldSpec` objects.
    """

    @property
    def ttype_code(self):
        return TType.STRUCT

    def to_wire(self, value):
        fields = deque()

        for field in self.fields:
            value = getattr(value, field.name, None)
            if value is None:
                continue
            fields.append(field.to_wire(value))

        return V.StructValue(fields)

    def from_wire(self, wire_value):
        kwargs = {}
        for field in self.fields:
            value = wire_value.get(field.id, field.spec.ttype_code)
            if value is None:
                continue
            kwargs[field.name] = field.spec.from_wire(value)

        # TODO For the case where cls fails to instantiate because a required
        # positional argument is missing, we know that the request was
        # invalid.
        return self.cls(**kwargs)

    def transform_dependencies(self, function):
        for field in self.fields:
            field.transform_dependencies(function)


class MapTypeSpec(TypeSpec):
    """
    :param TypeSpec kspec:
        TypeSpec of the keys in the map.
    :param TypeSpec vspec:
        TypeSpec of the values in the map.
    """

    __slots__ = ('kspec', 'vspec')

    def __init__(self, kspec, vspec):
        self.kspec = kspec
        self.vspec = vspec

    @property
    def ttype_code(self):
        return TType.MAP

    def to_wire(self, value):
        return V.MapValue(
            key_ttype=self.kspec.ttype_code,
            value_ttype=self.vspec.ttype_code,
            pairs=[
                (self.kspec.to_wire(k), self.vspec.to_wire(v))
                for k, v in value.items()
            ]
        )

    def from_wire(self, wire_value):
        return {
            self.kspec.from_wire(k): self.vspec.from_wire(v)
            for k, v in wire_value.pairs
        }

    def transform_dependencies(self, function):
        self.kspec = function(self.kspec)
        self.vspec = function(self.vspec)

    def __str__(self):
        return 'MapTypeSpec(kspec=%r, vspec=%r)' % (self.kspec, self.vspec)

    __repr__ = __str__


class SetTypeSpec(TypeSpec):
    """
    :param TypeSpec vspec:
        TypeSpec of values stored in the set.
    """

    __slots__ = ('vspec',)

    def __init__(self, vspec):
        self.vspec = vspec

    @property
    def ttype_code(self):
        return TType.SET

    def to_wire(self, value):
        return V.SetValue(
            value_ttype=self.vspec.ttype_code,
            values=[self.vspec.to_wire(v) for v in value],
        )

    def from_wire(self, wire_value):
        return set(
            self.vspec.from_wire(v) for v in wire_value.values
        )

    def transform_dependencies(self, function):
        self.vspec = function(self.vspec)

    def __str__(self):
        return 'SetTypeSpec(vspec=%r)' % self.vspec

    __repr__ = __str__


class ListTypeSpec(TypeSpec):
    """
    :param TypeSpec vspec:
        TypeSpec of values stored in the list.
    """

    __slots__ = ('vspec',)

    def __init__(self, vspec):
        self.vspec = vspec

    @property
    def ttype_code(self):
        return TType.LIST

    def to_wire(self, value):
        return V.ListValue(
            value_ttype=self.vspec.ttype_code,
            values=[self.vspec.to_wire(v) for v in value],
        )

    def from_wire(self, wire_value):
        return [self.vspec.from_wire(v) for v in wire_value.values]

    def transform_dependencies(self, function):
        self.vspec = function(self.vspec)

    def __str__(self):
        return 'ListTypeSpec(vspec=%r)' % self.vspec

    __repr__ = __str__
