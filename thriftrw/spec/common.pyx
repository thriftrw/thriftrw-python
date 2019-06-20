# Copyright (c) 2016 Uber Technologies, Inc.
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


def fields_eq(fields):
    """Generates an ``__eq__`` method.

    :param list fields:
        List of fields of the object to be compared.
    """
    def __eq__(self, other):
        return isinstance(other, self.__class__) and all(
            getattr(self, name) == getattr(other, name) for name in fields
        )
    return __eq__


def fields_str(cls_name, field_list, include_none=True):
    """Generates a ``__str__`` method.

    :param cls_name:
        Name of the class for which the method is being generated.
    :param list field_list:
        List of field_list of the class to be included in the output.
    :param bool include_none:
        Whether None attributes should be included in the output.
    """
    def __str__(self):
        fields = {}

        for name in field_list:
            # TODO use to_primitive?
            value = getattr(self, name)
            if include_none or value is not None:
                fields[name] = value

        return "%s(%r)" % (cls_name, fields)
    return __str__


def to_primitive_method(type_spec):
    """Generates the ``to_primitive`` method for types given the TypeSpec."""

    def to_primitive(self):
        return type_spec.to_primitive(self)

    return to_primitive


def from_primitive_classmethod():
    """Generates the ``from_primitive`` classmethod for types."""

    @classmethod
    def from_primitive(cls, prim_value):
        return cls.type_spec.from_primitive(prim_value)

    return from_primitive


def struct_hasher(spec):
    """Generates a ``__hash__`` method.

    :param list fields:
        List of fields of the object to be hashed.
    """
    def __hash__(self):
        return hash(
            tuple(
                getattr(self, field.name) for field in spec.fields
            )
        )
    return __hash__
