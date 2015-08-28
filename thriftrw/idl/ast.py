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

from collections import namedtuple

__all__ = [
    'Program',
    'Include',
    'Namespace',
    'Const',
    'Typedef',
    'Enum',
    'EnumItem',
    'Struct',
    'Union',
    'Exc',
    'Service',
    'Function',
    'Field',
    'PrimitiveType',
    'MapType',
    'SetType',
    'ListType',
    'DefinedType',
    'ConstValue',
    'ConstPrimitiveValue',
    'ConstReference',
    'ConstList',
    'ConstMap',
    'Annotation',
]


##############################################################################
# Program


class Program(namedtuple('Program', 'headers definitions')):
    """The top-level object representing the full Thrift IDL.

    The following attributes are available:

    .. py:attribute:: headers

        Collection of :py:class:`Include` and :py:class:`Namespace` objects.

    .. py:attribute:: definitions

        Collection of items of the following types.

        - :py:class:`Const`
        - :py:class:`Typedef`
        - :py:class:`Enum`
        - :py:class:`Struct`
        - :py:class:`Union`
        - :py:class:`Exc`
        - :py:class:`Service`
    """


##############################################################################
# Headers


class Include(namedtuple('Include', 'path lineno')):
    """A request to include the Thrift file at the given path.

    ::

        include "common.thrift"

    .. py:attribute:: path

        Path to the file to be included.
    """

    def apply(self, visitor):
        return visitor.visit_include(self)


class Namespace(namedtuple('Namespace', 'scope name lineno')):
    """Used to specify an alternative namespace for the given scope.

    ::

        namespace py my_service.generated

    .. py:attribute:: scope

        Scope to which this namespace rule applies. Can be a language
        specifier or '*' to apply to all languages.

    .. py:attribute:: name

        Namespace for the specified scope.
    """

    def apply(self, visitor):
        return visitor.visit_namespace(self)


##############################################################################
# Definitions


class Const(namedtuple('Const', 'name value_type value lineno')):
    """A constant defined in the Thrift IDL.

    ::

        const i32 DEFAULT_ID = 0;

    .. py:attribute:: name

        Name of the constant.

    .. py:attribute:: value_type

        Type of value held by the constant.

    .. py:attribute:: value

        Value specified for the constant.
    """

    def apply(self, visitor):
        return visitor.visit_const(self)


class Typedef(namedtuple('Typedef', 'name target_type annotations lineno')):
    """Typedefs define a new type which is an alias for another type.

    ::

        typedef string UUID

    .. py:attribute:: name

        Name of the new defined type.

    .. py:attribute:: target_type

        Type being aliased.

    .. py:attribute:: annotations

        Annotations for this type. See :py:class:`Annotation`.
    """

    def apply(self, visitor):
        return visitor.visit_typedef(self)


class Enum(namedtuple('Enum', 'name items annotations lineno')):
    """Enums define a new type which is a set of named integer values.

    ::

        enum Role {
            USER = 1,
            ADMIN,
        }

    .. py:attribute:: name

        Name of the enum type.

    .. py:attribute:: items

        Items defined in this Enum type. See :py:class:`EnumItem`.

    .. py:attribute:: annotations

        Annotations for this type. See :py:class:`Annotation`.
    """

    def apply(self, visitor):
        return visitor.visit_enum(self)


class EnumItem(namedtuple('EnumItem', 'name value annotations lineno')):
    """An item defined in an :py:class:`Enum` definition.

    .. py:attribute:: name

        Name of the item.

    .. py:attribute:: value

        Value specified for this item, if any. ``None`` othewise.

    .. py:attribute:: annotations

        Annotations for this item. See :py:class:`Annotation`.
    """


class Struct(namedtuple('Struct', 'name fields annotations lineno')):
    """A struct is a collection of named fields.

    .. py:attribute:: name

        Name of the struct.

    .. py:attribute:: fields

        Fields defined in the struct. See :py:class:`Field`.

    .. py:attribute:: annotations

        Annotations for this type. See :py:class:`Annotation`.
    """

    def apply(self, visitor):
        return visitor.visit_struct(self)


class Union(namedtuple('Union', 'name fields annotations lineno')):
    """A union is a sum of different types.

    .. py:attribute:: name

        Name of the union.

    .. py:attribute:: fields

        Fields defined in the union. See :py:class:`Field`.

    .. py:attribute:: annotations

        Annotations for this type. See :py:class:`Annotation`.
    """

    def apply(self, visitor):
        return visitor.visit_union(self)


class Exc(namedtuple('Exc', 'name fields annotations lineno')):
    """A Thrift exception definition.

    .. py:attribute:: name

        Name of the exception class.

    .. py:attribute:: fields

        Fields defined for the class. See :py:class:`Field`.

    .. py:attribute:: annotations

        Annotations for this type. See :py:class:`Annotation`.
    """

    def apply(self, visitor):
        return visitor.visit_exc(self)

# Can't use the name Exception because that will shadow the Exception class
# defined by Python.


class Service(
    namedtuple('Service', 'name functions parent annotations lineno')
):
    """A service definition.

    .. py:attribute:: name

        Name of the service.

    .. py:attribute:: functions

        Collection of function defined in the service. See
        :py:class:`Function`.

    .. py:attribute:: parent

        Name of the service that this service extends. ``None`` if this service
        doesn't have a parent service.

    .. py:attribute:: annotations

        Annotations for this service. See :py:class:`Annotation`.
    """

    def apply(self, visitor):
        return visitor.visit_service(self)


class Function(
    namedtuple(
        'Function',
        'name parameters return_type exceptions oneway annotations lineno'
    )
):
    """A function defined inside a service.

    .. py:attribute:: name

        Name of the function.

    .. py:attribute:: parameters

        Collection of parameters accepted by this method. See
        :py:class:`Field`.

    .. py:attribute:: return_type

        The type of value returned by this method.

    .. py:attribute:: exceptions

        Collection of exceptions raised by this method. See :py:class:`Field`.

    .. py:attribute:: oneway

        Whether this method is ``oneway`` or not.

    .. py:attribute:: annotations

        Annotations for this method. See :py:class:`Annotation`.
    """


class Field(
    namedtuple(
        'Field',
        'id name field_type requiredness default annotations lineno'
    )
):
    """A field defined inside a struct, union, exception, or parameter list.

    .. py:attribute:: id

        The numeric field identifier. `None` if not specified.

    .. py:attribute:: name

        Name of the field.

    .. py:attribute:: field_type

        Type of value held by the field.

    .. py:attribute:: requiredness

        ``True`` if this field was ``required``, ``False`` if ``optional``.
        ``None`` if required or optional was not specified.

    .. py:attribute:: default

        Default value of the field. ``None`` if not specified.

    .. py:attribute:: annotations

        Annotations for this field. See :py:class:`Annotation`.
    """

##############################################################################
# Types


class PrimitiveType(namedtuple('PrimitiveType', 'name annotations')):
    """Reference to primitive types.

    .. py:attribute:: name

        Name of the primitive type.

    .. py:attribute:: annotations

        Annotations for this type. See :py:class:`Annotation`.
    """

    def apply(self, visitor):
        return visitor.visit_primitive(self)


class MapType(namedtuple('MapType', 'key_type value_type annotations')):
    """A ``map<key, value>`` type.

    .. py:attribute:: key_type

        Type of the keys in the map.

    .. py:attribute:: value_type

        Type of the values in the map.

    .. py:attribute:: annotations

        Annotations for this type. See :py:class:`Annotation`.
    """

    def apply(self, visitor):
        return visitor.visit_map(self)


class SetType(namedtuple('SetType', 'value_type annotations')):
    """A ``set<item>`` type.

    .. py:attribute:: value_type

        Type of items in the set.

    .. py:attribute:: annotations

        Annotations for this type. See :py:class:`Annotation`.
    """

    def apply(self, visitor):
        return visitor.visit_set(self)


class ListType(namedtuple('ListType', 'value_type annotations')):
    """A ``list<item>`` type.

    .. py:attribute:: value_type

        Type of items in the list.

    .. py:attribute:: annotations

        Annotations for this type. See :py:class:`Annotation`.
    """

    def apply(self, visitor):
        return visitor.visit_list(self)


class DefinedType(namedtuple('DefinedType', 'name lineno')):
    """Reference to a type defined by the user.

    .. py:attribute:: name

        Name of the referenced type.
    """

    def apply(self, visitor):
        return visitor.visit_defined(self)


##############################################################################
# Constants

# TODO Move things that are sectioned like this into separate modules and
# explicitly specify their visitor interfaces.

class ConstValue(object):
    """Base class for constant value types."""

    def apply(self, visitor):
        raise NotImplementedError


class ConstPrimitiveValue(
    namedtuple('ConstPrimitiveValue', 'value lineno'), ConstValue
):
    """A complete constant value.

    .. py:attribute:: value

        Value held in this constant.
    """

    def apply(self, visitor):
        return visitor.visit_primitive(self)


class ConstReference(namedtuple('ConstReference', 'name lineno'), ConstValue):
    """Reference to another constant value or enum item.

    .. py:attribute:: name

        Name of the constant or enum item.
    """

    def apply(self, visitor):
        return visitor.visit_reference(self)


class ConstList(namedtuple('ConstList', 'values lineno'), ConstValue):
    """A list of constant values.

    .. py:attribute:: values

        Collection of ``ConstValue`` objects.
    """

    def apply(self, visitor):
        return visitor.visit_list(self)


class ConstMap(namedtuple('ConstList', 'pairs lineno'), ConstValue):
    """A map of constant values.

    .. py:attribute:: pairs

        Collection of pairs of ``ConstValue`` objects.
    """

    def apply(self, visitor):
        return visitor.visit_map(self)


##############################################################################
# Other


class Annotation(namedtuple('Annotation', 'name value lineno')):
    """Annotations for entities that can be annotated.

    They're usually in the form,::

        (foo = "bar", baz = "qux")

    For example,::

        struct User {
            1: string name (sensitive = "true");
        }

    .. py:attribute:: name

        Name of the annotation.

    .. py:attribute:: value

        Value specified for the annotation.
    """
