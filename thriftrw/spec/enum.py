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

from thriftrw.wire import TType
from thriftrw.wire.value import I32Value
from thriftrw.compile.exceptions import ThriftCompilerError

from . import check
from .base import TypeSpec

__all__ = ['EnumTypeSpec']


class EnumTypeSpec(TypeSpec):
    """TypeSpec for enum types.

    The surface for enum types is a class with the following:

    .. py:attribute:: type_spec

        :py:class:`EnumTypeSpec` for the type.

    .. py:attribute:: items

        A tuple of the names of all items in this enum.

    .. py:attribute:: values

        A tuple of the values of all items in this enum in the same order as
        ``items``.

    .. py:classmethod:: name_of(value)

        Finds the name of an enum item by its value.

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
    """

    __slots__ = ('name', 'items', 'values_to_names', 'linked', 'surface')

    ttype_code = TType.I32

    def __init__(self, name, items):
        assert name
        assert items is not None

        #: Name of the enum class.
        self.name = name

        #: Mapping of enum item names to item values.
        self.items = items

        values_to_names = {}
        for name, value in items.items():
            if value in values_to_names:
                dupe = values_to_names[value]
                raise ThriftCompilerError(
                    'Items "%s" and "%s" of enum "%s" have value "%d". '
                    'Enums items cannot share values.' % (
                        name, dupe, self.name, value
                    )
                )
            values_to_names[value] = name

        #: Mapping of enum item values to their names.
        self.values_to_names = values_to_names
        self.linked = False

        #: The surface for this spec.
        self.surface = None

    def link(self, scope):
        if not self.linked:
            self.linked = True
            self.surface = enum_cls(self)
        return self

    def to_wire(self, value):
        if value not in self.values_to_names:
            raise ValueError(
                '%r is not a valid value for enum "%s"' % (value, self.name)
            )
        return I32Value(value)

    def from_wire(self, wire_value):
        check.type_code_matches(self, wire_value)
        return wire_value.value

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

    def __eq__(self, other):
        return (
            self.name == other.name and
            self.items == other.items and
            self.linked == other.linked
        )

    def __str__(self):
        return 'EnumTypeSpec(name=%r, items=%r)' % (self.name, self.items)

    __repr__ = __str__


def enum_cls(enum_spec):
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
    return cls._VALUES_TO_NAMES.get(value)


def enum_docstring(name, items):
    item_section = '\n'.join(
        '-    %s = %s' % pair for pair in items
    )
    return '%s defines the following items:\n\n' % name + item_section
