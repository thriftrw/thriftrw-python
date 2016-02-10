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

from collections import defaultdict

from thriftrw.wire cimport ttype
from thriftrw._cython cimport richcompare
from thriftrw.wire.value cimport I32Value, Value
from .base cimport TypeSpec
from . cimport check

from ..errors import ThriftCompilerError

__all__ = ['EnumTypeSpec']


cdef class EnumTypeSpec(TypeSpec):
    """TypeSpec for enum types.

    .. py:attribute:: name

        Name of the enum class.

    .. py:attribute:: items

        Mapping of enum item names to item values.

    .. py:attribute:: values_to_names

        Mapping of enum item values to a list of enum item names with that
        value.

        .. versionchanged:: 1.1

            Changed to a list of names.

    .. py:attribute:: surface

        The surface for this spec.

    The `surface` for enum types is a class with the following:

    .. py:attribute:: type_spec

        :py:class:`EnumTypeSpec` for the type.

    .. py:attribute:: items

        A tuple of the names of all items in this enum.

    .. py:attribute:: values

        A tuple of the values of all items in this enum in the same order as
        ``items``.

    .. py:classmethod:: name_of(value)

        Finds the name of an enum item by its value. If multiple enum items
        have this value, any of the matching item names could can be returned.

        :param int value:
            A value for an item defined in this enum.
        :returns:
            Name of the item with that value or None if no such item exists.

    And one attribute for each enum item that has the same name as the
    attribute and points to the value for that item.

    Given the definition,::

        enum Role {
            User, Admin
        }

    The generated class is roughly equivalent to,

    .. code-block:: python

        class Role(object):
            User = 0
            Admin = 1

            items = ('User', 'Admin')
            values = (0, 1)

            type_spec = # ...

            def name_of(self, value):
                # ...

    .. versionchanged:: 1.1

        Added support for multiple enum items with the same value.
    """

    ttype_code = ttype.I32

    def __init__(self, name, items):
        assert name
        assert items is not None

        self.name = unicode(name)
        self.items = items

        values_to_names = defaultdict(lambda: [])
        for name, value in items.items():
            values_to_names[value].append(name)

        self.values_to_names = values_to_names
        self.linked = False
        self.surface = None

    cpdef TypeSpec link(self, scope):
        if not self.linked:
            self.linked = True
            self.surface = enum_cls(self, scope)
        return self

    cpdef Value to_wire(self, object value):
        return I32Value(value)

    cpdef object to_primitive(self, object value):
        return value

    cpdef object from_wire(self, Value wire_value):
        check.type_code_matches(self, wire_value)
        return wire_value.value

    cpdef object from_primitive(self, object prim_value):
        return prim_value

    cpdef void validate(self, object instance) except *:
        if instance not in self.values_to_names:
            raise ValueError(
                '%r is not a valid value for enum "%s"' % (instance, self.name)
            )

    @classmethod
    def compile(cls, enum):
        items = {}

        # TODO check for int32 overflow.

        prev = -1
        for item in enum.items:
            value = item.value
            if value is None:
                value = prev + 1
            prev = value

            if item.name in items:
                raise ThriftCompilerError(
                    'Enum entry "%s.%s" on line %d has duplicates.' %
                    (enum.name, item.name, item.lineno)
                )

            items[item.name] = value

        return cls(enum.name, items)

    def __richcmp__(EnumTypeSpec self, EnumTypeSpec other not None, int op):
        return richcompare(op, [
            (self.name, other.name),
            (self.items, other.items),
        ])

    def __str__(self):
        return 'EnumTypeSpec(name=%r, items=%r)' % (self.name, self.items)

    def __repr__(self):
        return str(self)


def enum_cls(enum_spec, scope):
    """Generates a class for the given EnumTypeSpec.

    :param EnumTypeSpec enum_spec:
        EnumTypeSpec for which the class is being generated.
    """
    enum_dct = {}

    for name, item in enum_spec.items.items():
        enum_dct[name] = item

    keys, values = zip(*enum_spec.items.items())

    enum_dct['_VALUES_TO_NAMES'] = enum_spec.values_to_names
    enum_dct['items'] = tuple(keys)
    enum_dct['values'] = tuple(values)
    enum_dct['name_of'] = name_of
    enum_dct['type_spec'] = enum_spec
    enum_dct['__thrift_module__'] = scope.module
    enum_dct['__slots__'] = ()
    enum_dct['__doc__'] = enum_docstring(
        enum_spec.name, enum_spec.items.items()
    )

    return type(str(enum_spec.name), (object,), enum_dct)


@classmethod
def name_of(cls, value):
    """Returns the name of the enum item with the given value.

    :param int value:
        Enum item value
    :returns:
        Name of the corresponding enum item or None if no such item exists.
    """
    names = cls._VALUES_TO_NAMES.get(value)
    if names:
        return names[0]
    return None


def enum_docstring(name, items):
    item_section = '\n'.join(
        '-    %s = %s' % pair for pair in items
    )
    return '%s defines the following items:\n\n' % name + item_section
