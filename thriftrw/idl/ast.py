from __future__ import absolute_import, unicode_literals, print_function

from collections import namedtuple


class Node(object):
    PROGRAM = 'PROGRAM'
    INCLUDE = 'INCLUDE'
    NAMESPACE = 'NAMESPACE'
    CONST = 'CONST'
    TYPEDEF = 'TYPEDEF'
    ENUM = 'ENUM'
    STRUCT = 'STRUCT'
    UNION = 'UNION'
    EXCEPTION = 'EXCEPTION'
    SERVICE = 'SERVICE'


##############################################################################
# Program


class Program(namedtuple('Program', 'headers definitions')):
    """The top-level object representing the full Thrift IDL.

    The following attributes are available:

    ``headers``
        Collection of :py:class:`Include` and :py:class:`Namespace` objects.

    ``definitions``
        Collection of items of the following types.

        - :py:class:`Const`
        - :py:class:`Typedef`
        - :py:class:`Enum`
        - :py:class:`Struct`
        - :py:class:`Union`
        - :py:class:`Exc`
        - :py:class:`Service`
    """

    TYPE = Node.PROGRAM

##############################################################################
# Headers


class Include(namedtuple('Include', 'path lineno')):
    """A request to include the Thrift file at the given path.

    ::

        include "common.thrift"

    ``path``
        Path to the file to be included.
    """

    TYPE = Node.INCLUDE


class Namespace(namedtuple('Namespace', 'scope name lineno')):
    """Used to specify an alternative namespace for the given scope.

    ::

        namespace py my_service.generated

    ``scope``
        Scope to which this namespace rule applies. Can be a language
        specifier or '*' to apply to all languages.
    ``name``
        Namespace for the specified scope.
    """

    TYPE = Node.NAMESPACE


##############################################################################
# Definitions


class Const(namedtuple('Const', 'name value_type value lineno')):
    """A constant defined in the Thrift IDL.

    ::

        const i32 DEFAULT_ID = 0;

    ``name``
        Name of the constant.
    ``value_type``
        Type of value held by the constant.
    ``value``
        Value specified for the constant.
    """

    TYPE = Node.CONST


class Typedef(namedtuple('Typedef', 'name target_type annotations lineno')):
    """Typedefs define a new type which is an alias for another type.

    ::

        typedef string UUID

    ``name``
        Name of the new defined type.
    ``target_type``
        Type being aliased.
    ``annotations``
        Annotations for this type. See :py:class:`Annotation`.
    """

    TYPE = Node.TYPEDEF


class Enum(namedtuple('Enum', 'name items annotations lineno')):
    """Enums define a new type which is a set of named integer values.

    ::

        enum Role {
            USER = 1,
            ADMIN,
        }

    ``name``
        Name of the enum type.
    ``items``
        Items defined in this Enum type. See :py:class:`EnumItem`.
    ``annotations``
        Annotations for this type. See :py:class:`Annotation`.
    """

    TYPE = Node.ENUM


class EnumItem(namedtuple('EnumItem', 'name value annotations lineno')):
    """An item defined in an :py:class:`Enum` definition.

    ``name``
        Name of the item.
    ``value``
        Value specified for this item, if any. ``None`` othewise.
    ``annotations``
        Annotations for this item. See :py:class:`Annotation`.
    """


class Struct(namedtuple('Struct', 'name fields annotations lineno')):
    """A struct is a collection of named fields.

    ``name``
        Name of the struct.
    ``fields``
        Fields defined in the struct. See :py:class:`Field`.
    ``annotations``
        Annotations for this type. See :py:class:`Annotation`.
    """

    TYPE = Node.STRUCT


class Union(namedtuple('Union', 'name fields annotations lineno')):
    """A union is a sum of different types.

    ``name``
        Name of the union.
    ``fields``
        Fields defined in the union. See :py:class:`Field`.
    ``annotations``
        Annotations for this type. See :py:class:`Annotation`.
    """

    TYPE = Node.UNION


class Exc(namedtuple('Exc', 'name fields annotations lineno')):
    """A Thrift exception definition.

    ``name``
        Name of the exception class.
    ``fields``
        Fields defined for the class. See :py:class:`Field`.
    ``annotations``
        Annotations for this type. See :py:class:`Annotation`.
    """

    TYPE = Node.EXCEPTION

# Can't use the name Exception because that will shadow the Exception class
# defined by Python.


class Service(
    namedtuple('Service', 'name functions parent annotations lineno')
):
    """A service definition.

    ``name``
        Name of the service.
    ``functions``
        Collection of function defined in the service. See
        :py:class:`Function`.
    ``parent``
        Name of the service that this service extends. ``None`` if this service
        doesn't have a parent service.
    ``annotations``
        Annotations for this service. See :py:class:`Annotation`.
    """

    TYPE = Node.SERVICE


class Function(
    namedtuple(
        'Function',
        'name parameters return_type exceptions oneway annotations lineno'
    )
):
    """A function defined inside a service.

    ``name``
        Name of the function.
    ``parameters``
        Collection of parameters accepted by this method. See
        :py:class:`Field`.
    ``return_type``
        The type of value returned by this method.
    ``exceptions``
        Collection of exceptions raised by this method. See :py:class:`Field`.
    ``oneway``
        Whether this method is ``oneway`` or not.
    ``annotations``
        Annotations for this method. See :py:class:`Annotation`.
    """


class Field(
    namedtuple(
        'Field',
        'id name field_type requiredness default annotations lineno'
    )
):
    """A field defined inside a struct, union, exception, or parameter list.

    ``id``
        The numeric field identifier. `None` if not specified.
    ``name``
        Name of the field.
    ``field_type``
        Type of value held by the field.
    ``requiredness``
        ``True`` if this field was ``required``, ``False`` if ``optional``.
        ``None`` if required or optional was not specified.
    ``default``
        Default value of the field. ``None`` if not specified.
    ``annotations``
        Annotations for this field. See :py:class:`Annotation`.
    """

##############################################################################
# Types


class PrimitiveType(namedtuple('PrimitiveType', 'name annotations')):
    """Reference to primitive types.

    ``name``
        Name of the primitive type.
    ``annotations``
        Annotations for this type. See :py:class:`Annotation`.
    """


class MapType(namedtuple('MapType', 'key_type value_type annotations')):
    """A ``map<key, value>`` type.

    ``key_type``
        Type of the keys in the map.
    ``value_type``
        Type of the values in the map.
    ``annotations``
        Annotations for this type. See :py:class:`Annotation`.
    """


class SetType(namedtuple('SetType', 'value_type annotations')):
    """A ``set<item>`` type.

    ``value_type``
        Type of items in the set.
    ``annotations``
        Annotations for this type. See :py:class:`Annotation`.
    """


class ListType(namedtuple('ListType', 'value_type annotations')):
    """A ``list<item>`` type.

    ``value_type``
        Type of items in the list.
    ``annotations``
        Annotations for this type. See :py:class:`Annotation`.
    """


class DefinedType(namedtuple('DefinedType', 'name lineno')):
    """Reference to a type defined by the user.

    ``name``
        Name of the referenced type.
    """


##############################################################################
# Constants


class ConstValue(namedtuple('ConstValue', 'value lineno')):
    """A complete constant value.

    ``value``
        Value held in this constant.
    """


class ConstReference(namedtuple('ConstReference', 'name lineno')):
    """Reference to another constant value or enum item.

    ``name``
        Name of the constant or enum item.
    """


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

    ``name``
        Name of the annotation.
    ``value``
        Value specified for the annotation.
    """
