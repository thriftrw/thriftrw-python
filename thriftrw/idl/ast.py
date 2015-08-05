from __future__ import absolute_import, unicode_literals, print_function

from collections import namedtuple


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

##############################################################################
# Headers


class Include(namedtuple('Include', 'path')):
    """A request to include the Thrift file at the given path.

    ::

        include "common.thrift"

    ``path``
        Path to the file to be included.
    """


class Namespace(namedtuple('Namespace', 'scope name')):
    """Used to specify an alternative namespace for the given scope.

    ::

        namespace py my_service.generated

    ``scope``
        Scope to which this namespace rule applies. Can be a language
        specifier or '*' to apply to all languages.
    ``name``
        Namespace for the specified scope.
    """


class Const(namedtuple('Const', 'name value_type value')):
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

##############################################################################
# Definitions


class Typedef(namedtuple('Typedef', 'name target_type annotations')):
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


class Enum(namedtuple('Enum', 'name items annotations')):
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


class EnumItem(namedtuple('EnumItem', 'name value annotations')):
    """An item defined in an :py:class:`Enum` definition.

    ``name``
        Name of the item.
    ``value``
        Value specified for this item, if any. ``None`` othewise.
    ``annotations``
        Annotations for this item. See :py:class:`Annotation`.
    """


class Struct(namedtuple('Struct', 'name fields annotations')):
    """A struct is a collection of named fields.

    ``name``
        Name of the struct.
    ``fields``
        Fields defined in the struct. See :py:class:`Field`.
    ``annotations``
        Annotations for this type. See :py:class:`Annotation`.
    """


class Union(namedtuple('Union', 'name fields annotations')):
    """A union is a sum of different types.

    ``name``
        Name of the union.
    ``fields``
        Fields defined in the union. See :py:class:`Field`.
    ``annotations``
        Annotations for this type. See :py:class:`Annotation`.
    """


class Exc(namedtuple('Exc', 'name fields annotations')):
    """A Thrift exception definition.

    ``name``
        Name of the exception class.
    ``fields``
        Fields defined for the class. See :py:class:`Field`.
    ``annotations``
        Annotations for this type. See :py:class:`Annotation`.
    """

# Can't use the name Exception because that will shadow the Exception class
# defined by Python.


class Service(namedtuple('Service', 'name functions parent annotations')):
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


class Function(
    namedtuple(
        'Function',
        'name parameters return_type exceptions oneway annotations'
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
    namedtuple('Field', 'id name field_type requiredness default annotations')
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
# Basic types


class BoolType(namedtuple('BoolType', 'annotations')):
    """A ``bool`` type.

    ``annotations``
        Annotations for this type. See :py:class:`Annotation`.
    """


class ByteType(namedtuple('ByteType', 'annotations')):
    """A ``byte`` type.

    ``annotations``
        Annotations for this type. See :py:class:`Annotation`.
    """


class I16Type(namedtuple('I16Type', 'annotations')):
    """A ``i16`` type.

    ``annotations``
        Annotations for this type. See :py:class:`Annotation`.
    """


class I32Type(namedtuple('I32Type', 'annotations')):
    """A ``i32`` type.

    ``annotations``
        Annotations for this type. See :py:class:`Annotation`.
    """


class I64Type(namedtuple('I64Type', 'annotations')):
    """A ``i64`` type.

    ``annotations``
        Annotations for this type. See :py:class:`Annotation`.
    """


class DoubleType(namedtuple('DoubleType', 'annotations')):
    """A ``double`` type.

    ``annotations``
        Annotations for this type. See :py:class:`Annotation`.
    """


class StringType(namedtuple('StringType', 'annotations')):
    """A ``string`` type.

    ``annotations``
        Annotations for this type. See :py:class:`Annotation`.
    """


class BinaryType(namedtuple('BinaryType', 'annotations')):
    """A ``binary`` type.

    ``annotations``
        Annotations for this type. See :py:class:`Annotation`.
    """


##############################################################################
# Container types


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


class DefinedType(namedtuple('DefinedType', 'name')):
    """Reference to a type defined by the user.

    ``name``
        Name of the referenced type.
    """

##############################################################################
# Constants


class ConstValue(namedtuple('ConstValue', 'value')):
    """A complete constant value.

    ``value``
        Value held in this constant.
    """


class ConstReference(namedtuple('ConstReference', 'name')):
    """Reference to another constant value or enum item.

    ``name``
        Name of the constant or enum item.
    """


##############################################################################
# Other


class Annotation(namedtuple('Annotation', 'name value')):
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
