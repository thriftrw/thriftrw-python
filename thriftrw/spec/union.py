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
from thriftrw.wire.value import StructValue
from thriftrw.compile.exceptions import ThriftCompilerError

from . import check
from . import common
from .base import TypeSpec
from .struct import FieldSpec

__all__ = ['UnionTypeSpec', 'FieldSpec']


class UnionTypeSpec(TypeSpec):
    """Spec for Thrift unions.

    The surface for union types is a class with the following:

    .. py:attribute:: type_spec

        :py:class:`UnionTypeSpec` for the type.

    .. py:method:: __init__(self, *args, **kwargs)

        Accepts all fields of the unions as keyword arguments but only one of
        them is allowed to be non-None. Positional arguments are not accepted.

    And obvious definitions of ``__str__`` and ``__eq__``.

    Given the definition,::

        union Body {
            1: string plainText
            2: binary richText
        }

    A class roughly equivalent to the following is generated,

    .. code-block:: python

        class Body(object):

            __slots__ = ('plainText', 'richText')

            def __init__(self, plainText=None, richText=None):
                # Only one of plainText and richText may be non-None.
                # ...
    """

    __slots__ = ('name', 'fields', 'linked', 'surface', 'allow_empty')

    ttype_code = TType.STRUCT

    def __init__(self, name, fields, allow_empty=None):
        self.name = name
        self.fields = fields
        self.linked = False
        self.surface = None
        self.allow_empty = allow_empty

    def link(self, scope):
        if not self.linked:
            self.linked = True
            self.fields = [field.link(scope) for field in self.fields]
            self.surface = union_cls(self, scope)
        return self

    @classmethod
    def compile(cls, union):
        fields = []
        ids = set()
        names = set()
        for field in union.fields:
            if field.name in names:
                raise ThriftCompilerError(
                    'Field "%s" of union "%s" on line %d has duplicates.' %
                    (field.name, union.name, field.lineno)
                )
            names.add(field.name)

            if field.id in ids:
                raise ThriftCompilerError(
                    'Field ID "%d" of union "%s" on line %d '
                    'has already been used.' % (
                        field.id, union.name, field.lineno
                    )
                )
            ids.add(field.id)

            if field.requiredness is not None:
                raise ThriftCompilerError(
                    'Field "%s" of union "%s" on line %d is "%s". '
                    'Unions cannot specify requiredness. '
                    % (
                        field.name,
                        union.name,
                        field.lineno,
                        'required' if field.requiredness else 'optional',
                    )
                )

            if field.default is not None:
                raise ThriftCompilerError(
                    'Field "%s" of union "%s" on line %d has a default value.'
                    ' Fields of unions cannot have default values. '
                    % (field.name, union.name, field.lineno)
                )

            fields.append(FieldSpec.compile(
                field=field,
                struct_name=union.name,
                require_requiredness=False,
            ))
        return cls(union.name, fields)

    def to_wire(self, union):
        check.instanceof_surface(self, union)
        fields = []

        for field in self.fields:
            value = getattr(union, field.name)
            if value is None:
                continue
            fields.append(field.to_wire(value))

        return StructValue(fields)

    def from_wire(self, wire_value):
        check.type_code_matches(self, wire_value)
        kwargs = {}
        for field in self.fields:
            field_value = wire_value.get(field.id, field.spec.ttype_code)
            if field_value is None:
                continue
            kwargs[field.name] = field.from_wire(field_value)

        # TODO For the case where cls fails to instantiate because a required
        # positional argument is missing, we know that the request was
        # invalid.
        return self.surface(**kwargs)

    def __str__(self):
        return 'UnionTypeSpec(name=%r, fields=%r)' % (self.name, self.fields)

    __repr__ = __str__

    def __eq__(self, other):
        return (
            self.name == other.name and
            self.fields == other.fields and
            self.linked == other.linked
        )


def union_init(cls_name, fields, allow_empty):
    """Generates the ``__init__`` method for unions.

    :param cls_name:
        Name of the class.
    :param fields:
        Collection of fields on the union.
    :param allow_empty:
        Whether a union with no values assigned is allowed.
    """

    def __init__(self, *args, **kwargs):
        if args:
            raise TypeError(
                '%s() does not accept any positional arguments (%d given)'
                % (cls_name, len(args))
            )

        assigned = None

        for field in fields:
            value = None

            if field in kwargs:
                value = kwargs.pop(field)

            setattr(self, field, value)

            if value is not None:
                if assigned is not None:
                    raise TypeError(
                        '%s() received multiple values, "%s" and "%s". '
                        'Unions can have at most one field populated. '
                        % (cls_name, assigned, field)
                    )
                else:
                    assigned = field

        if kwargs:
            # Too many kwargs given.
            for name in kwargs:
                raise TypeError(
                    '%s() got an unexpected keyword argument "%s"'
                    % (cls_name, name)
                )

        if assigned is None and fields and not allow_empty:
            raise TypeError(
                '%s() did not receive any values. '
                'Exactly one non-None value is required.'
                % cls_name
            )

    return __init__


def union_docstring(cls_name, fields):
    """Generates a docstring for generated unions."""

    fields_section = (
        '%s is a union of the following fields. '
        'Exactly one of them must be provided.\n\n' % cls_name
    ) + '\n'.join('-   %s' % name for name in fields)

    params = ', '.join('%s=None' % name for name in fields)
    header = '%s(%s)' % (cls_name, params)

    return header + '\n\n' + fields_section


def union_cls(union_spec, scope):
    """Generates a class for a union.

    The generated class has the following attributes:

    ``type_spec``
        Attribute pointing to the ``TypeSpec`` for the type.

    The ``__init__`` method of the class accepts all fields of the union as
    keyword arguments, and allows only one of them to be non-None.

    A ``__str__`` method that returns which field is populated and with what
    value is also added to the class.

    :param UnionTypeSpec union_spec:
        Spec of the union.
    :param thriftrw.compile.Scope scope:
        Compilation scope
    """
    field_names = set(field.name for field in union_spec.fields)

    union_dct = {}
    union_dct['type_spec'] = union_spec
    union_dct['__slots__'] = tuple(field_names)
    union_dct['__init__'] = union_init(
        union_spec.name, field_names, union_spec.allow_empty
    )
    union_dct['__str__'] = common.fields_str(
        union_spec.name, field_names, False
    )
    union_dct['__repr__'] = union_dct['__str__']
    union_dct['__eq__'] = common.fields_eq(field_names)
    union_dct['__doc__'] = union_docstring(
        union_spec.name, field_names
    )

    return type(str(union_spec.name), (object,), union_dct)
