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

from .base import TypeSpec

__all__ = ['EnumTypeSpec']


class EnumTypeSpec(TypeSpec):
    """TypeSpec for enum types.

    :ivar name:
        Name of the enum
    :ivar items:
        Mapping of enum item names to item values.
    :ivar surface:
        The generated Enum class.
    """

    __slots__ = ('name', 'items', 'values_to_names', 'linked', 'surface')

    ttype_code = TType.I32

    def __init__(self, name, items):
        """Initialize an EnumTypeSpec.

        :param name:
            Name of the enum class
        :param items:
            Mapping of enum item name to item value
        """
        assert name
        assert items is not None

        self.name = name
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

        self.values_to_names = values_to_names
        self.linked = False
        self.surface = None

    def link(self, scope):
        if not self.linked:
            self.linked = True
            self.surface = enum_cls(self)
        return self

    def to_wire(self, value):
        return I32Value(value)

    def from_wire(self, wire_value):
        return wire_value.value

    @classmethod
    def compile(cls, enum):
        """Compiles an Enum AST into an EnumTypeSpec.

        :param thriftrw.idl.Enum enum:
            Enum AST
        """
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

    def __str__(self):
        return 'EnumTypeSpec(name=%r, items=%r)' % (self.name, self.items)

    __repr__ = __str__


def enum_cls(enum_spec):
    """Generates a class for the given EnumTypeSpec.

    Generated classes have the following attributes and methods.


    ``items``
        An attribute which is a tuple of all items defined for that Enum.
    ``name_of(value)``
        A method which takes an enum value and returns the name of the
        corresponding enum item.
    ``type_spec``
        Points back to the EnumTypeSpec.

    :param EnumTypeSpec enum_spec:
        EnumTypeSpec for which the class is being generated.
    """
    enum_dct = {}

    for name, item in enum_spec.items.items():
        enum_dct[name] = item

    enum_dct['_VALUES_TO_NAMES'] = enum_spec.values_to_names
    enum_dct['items'] = tuple(enum_spec.items.keys())
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
