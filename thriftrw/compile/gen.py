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

from collections import deque

from .exceptions import ThriftCompilerError


@classmethod
def enum_name_of(cls, value):
    """Returns the name of the enum item with the given value.

    :param int value:
        Enum item value.
    :returns:
        Name of the corresponding enum item, or None if no such item exists.
    """
    return cls._VALUES_TO_NAMES.get(value)


def enum_cls(enum, spec):
    """Generate a class for the given enum.

    Generated clasess have the following attributes and methods:

    ``items``
        An attribute which is a tuple of all items defined for that Enum.
    ``name_of(value)``
        A method which takes an enum value and returns the name of the
        corresponding enum item.
    ``type_spec``
        Attribute pointing to the ``TypeSpec`` for the type.

    :param thriftrw.idl.Enum enum:
        AST definition of an enum.
    :param thriftrw.compile.spec.TypeSpec spec:
        Type specification of the values.
    :returns:
        A class for the Enum item.
    """
    item_names = deque()
    values_to_names = {}
    enum_dct = {}

    prev = -1
    for item in enum.items:
        value = item.value
        if value is None:
            value = prev + 1
        prev = value

        if item.name in enum_dct:
            raise ThriftCompilerError(
                'Enum entry "%s.%s" on line %d has duplicates.' %
                (enum.name, item.name, item.lineno)
            )

        if value in values_to_names:
            dupe = values_to_names[value]
            raise ThriftCompilerError(
                'Items "%s" and "%s" of enum "%s" share the same value: %d' %
                (item.name, dupe, enum.name, value)
            )

        item_names.append(item.name)
        enum_dct[item.name] = value
        values_to_names[value] = item.name

    # TODO make sure that these names weren't used by the enum items.

    # TODO declare a __new__ method that does something reasonable. Either
    # prevent instantiation, or act as name_of and its inverse based on
    # argument type.

    enum_dct['_VALUES_TO_NAMES'] = values_to_names
    enum_dct['items'] = tuple(item_names)
    enum_dct['name_of'] = enum_name_of
    enum_dct['type_spec'] = spec
    enum_dct['__slots__'] = ()

    return type(enum.name, (object,), enum_dct)


def struct_init(cls_name, field_names, field_defaults):
    """Generate the ``__init__`` method for structs.

    ``field_names`` is a list or tuple of field names for the constructor
    in-order. ``field_defaults`` is a list or tuple of default values for the
    last ``len(field_defaults)`` fields in-order.

    That is, for a signature like, ``f(a, b, c=1, d=2)``, ``field_names`` is
    ``('a', 'b', 'c', 'd')`` and ``field_defaults`` is ``(1, 2)``.

    :param cls_name:
        Name of the class. This is used for error messages.
    :param field_names:
        List or tuple of field names of the struct.
    :param field_defaults:
        List or tuple of default values for the last ``len(field_defaults)``
        fields. For optional fields with no default value, ``field_defaults``
        should have a ``None`` default.
    :returns:
        Implementation of the ``__init__`` method for that struct.
    """
    field_defaults = field_defaults or ()

    # Number of fields on the struct. We can't accept more than this many
    # arguments.
    num_fields = len(field_names)

    # Number of fields with default values.
    num_defaults = len(field_defaults)

    assert num_defaults <= num_fields, 'Too many defaults provided.'

    # The last num_defaults fields have default values, so all other fields
    # must have arguments passed in.
    num_required = num_fields - num_defaults

    def __init__(self, *args, **kwargs):
        num_args = len(args)
        num_kwargs = len(kwargs)
        num_total = num_args + num_kwargs

        # This argument binding implementation was adapted from
        # inspect.getcallargs() with adjustments for our requirements of
        # non-None fields.

        # TODO pull out argument binding logic into separate function
        # elsewhere.

        if num_total < num_required:
            raise TypeError(
                '%s() takes at least %d arguments (%d given)' % (
                    cls_name, num_required + 1, num_total + 1
                    # + 1 for 'self'
                )
            )

        if num_total > num_fields:
            raise TypeError(
                '%s() takes at most %d arguments (%d given)' % (
                    cls_name, num_fields + 1, num_total + 1
                    # + 1 for 'self'
                )
            )

        # Keeps track of fields yet to be assigned.
        unassigned = set(field_names)

        # Assign positional arguments.
        for name, value in zip(field_names, args):
            if value is not None:
                setattr(self, name, value)
                unassigned.remove(name)

        # Assign named arguments.
        for name in field_names:
            # We go over all field names instead of just the remaining ones so
            # that we can detect if any of the positional arguments had
            # another value specified in kwargs. That's user error and we
            # should blow up in that case.
            if name not in kwargs:
                continue
            if name not in unassigned:
                raise TypeError(
                    '%s() got multiple values for keyword argument '
                    '"%s"' % (cls_name, name)
                )
            value = kwargs.pop(name)
            if value is not None:
                setattr(self, name, value)
                unassigned.remove(name)

        # Add defaults
        if field_defaults:
            default_values = zip(field_names[-num_defaults:], field_defaults)
            for name, value in default_values:
                if name in unassigned:
                    setattr(self, name, value)
                    unassigned.remove(name)

        # If anything was left unassigned, blow up.
        if unassigned:
            raise ValueError(
                'Field(s) %r require non-None values.' % list(unassigned)
            )

        if kwargs:
            # Too many kwargs given.
            for name in kwargs:
                raise TypeError(
                    '%s() got an unexpected keyword argument "%s"'
                    % (cls_name, name)
                )

    # TODO reasonable docstring
    return __init__


def struct_str(cls_name, field_names):
    """Generate a ``__str__`` method for a struct."""

    def __str__(self):
        fields = {
            name: getattr(self, name, None) for name in field_names
        }
        return "%s(%r)" % (cls_name, fields)

    return __str__


def struct_cls(struct_name, struct_fields, struct_spec, const_resolver,
               base_cls=None, require_requiredness=True):
    """Generate a class for the given struct.

    The generated class has the following attributes:

    ``type_spec``
        Attribute pointing to the ``TypeSpec`` for the type.

    The ``__init__`` method of the class accepts all fields of the struct as
    arguments. Required arguments are placed first and may be specified as
    positional arguments (in the same order as they appear in the IDL).
    Optional arguments and required arguments with default values are placed
    after that.

    A ``__str__`` method that returns the contents of all fields of the struct
    is also added to the class.

    :param struct_name:
        Name of the struct.
    :param struct_fields:
        Collection of ``thriftrw.idl.Field`` objects.
    :param thriftrw.compile.spec.TypeSpec struct_spec:
        Type specification of the struct.
    :param thriftrw.compile.const.ConstValueResolver const_resolver:
        ConstValueResolver used to resolve values of field defaults.
    :param base_cls:
        Base class of the generated struct. Defaults to ``object``.
    :param require_requiredness:
        Whether fields must specify requireness explicitly. True by default.
    :returns:
        A class for the Struct.
    """
    base_cls = base_cls or object
    slots = set()

    required_fields = []
    optional_fields = []
    field_defaults = []

    for field in struct_fields:

        if field.name in slots:
            raise ThriftCompilerError(
                'Field "%s" of struct "%s" on line %d has duplicates.' %
                (field.name, struct_name, field.lineno)
            )
        slots.add(field.name)

        if field.requiredness is None and require_requiredness:
            raise ThriftCompilerError(
                'Field "%s" of "%s" on line %d does not explicitly specify '
                'requiredness. Please specify whether the field is optional '
                'or required in the IDL.'
                % (field.name, struct_name, field.lineno)
            )

        default = None
        if field.default is not None:
            # Resolve the default value.
            default = const_resolver.resolve(field.default)

        if field.requiredness and default is None:
            # required fields that have default values are optional as far as
            # the constructor is concerned.
            required_fields.append(field.name)
        else:
            optional_fields.append(field.name)
            field_defaults.append(default)

    field_names = required_fields + optional_fields

    struct_dct = {}
    struct_dct['type_spec'] = struct_spec
    struct_dct['__slots__'] = tuple(slots)
    struct_dct['__init__'] = struct_init(
        struct_name,
        field_names,
        field_defaults,
    )
    struct_dct['__str__'] = struct_str(struct_name, field_names)
    struct_dct['__repr__'] = struct_dct['__str__']

    return type(struct_name, (base_cls,), struct_dct)


def exception_cls(exc_name, exc_fields, spec, const_resolver):
    """Generate a class from the given AST definition of the exception.

    :param exc_name:
        Name of the exception class.
    :param exc_fields:
        Collection of ``thriftrw.idl.Field`` objects.
    :param thriftrw.compile.spec.TypeSpec spec:
        TypeSpec of the exception.
    :param thriftrw.compile.const.ConstValueResolver const_resolver:
        ConstValueResolver used to resolve values of field defaults.
    """
    struct = struct_cls(exc_name, exc_fields, spec, const_resolver, Exception)
    struct_init = struct.__init__

    def __init__(self, *args, **kwargs):
        Exception.__init__(self)
        struct_init(self, *args, **kwargs)

    struct.__init__ = __init__
    return struct


def union_init(cls_name, fields):
    """Generates the ``__init__`` method for unions.

    :param cls_name:
        Name of the class.
    :param fields:
        Collection of fields on the union.
    """

    def __init__(self, *args, **kwargs):
        if args:
            raise TypeError(
                '%s() does not accept any position arguments (%d given)'
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

        if assigned is None:
            raise TypeError(
                '%s() did not receive any values. '
                'Exactly one non-None value is required.'
                % cls_name
            )

    return __init__


def union_str(cls_name, fields):
    """Generates the ``__str__`` method for unions.

    :param cls_name:
        Name of the class.
    :param fields:
        Collection of fields on the union.
    """

    def __str__(self):
        field_name = None
        field_value = None

        for name in fields:
            value = getattr(self, name, None)
            if value is not None:
                field_name = name
                field_value = value
                break

        return '%s(%s=%r)' % (cls_name, field_name, field_value)

    return __str__


def union_cls(union_name, union_fields, spec, base_cls=None):
    """Generate a class for the given union.

    The generated class has the following attributes:

    ``type_spec``
        Attribute pointing to the ``TypeSpec`` for the type.

    The ``__init__`` method of the class accepts all fields of the union as
    keyword arguments, and allows only one of them to be non-None.

    A ``__str__`` method that returns which field is populated and with what
    value is also added to the class.

    :param union_name:
        Name of the union class.
    :param union_fields:
        Collection of ``thriftrw.idl.Field`` objects.
    :param thriftrw.compile.spec.TypeSpec spec:
        Type specification of the union.
    :param base_cls:
        Base class of the generated union. Defaults to ``object``.
    :returns:
        A class for the union.
    """
    base_cls = base_cls or object
    field_names = set()

    for field in union_fields:

        if field.name in field_names:
            raise ThriftCompilerError(
                'Field "%s" of struct "%s" on line %d has duplicates.' %
                (field.name, union_name, field.lineno)
            )
        field_names.add(field.name)

        if field.requiredness is not None:
            raise ThriftCompilerError(
                'Field "%s" of union "%s" on line %d is specified as "%s". '
                'Unions cannot specify requiredness. '
                'Please remove requiredness for %s.%s from the IDL.'
                % (
                    field.name,
                    union_name,
                    field.lineno,
                    'required' if field.requiredness else 'optional',
                    union_name,
                    field.name
                )
            )

        if field.default is not None:
            raise ThriftCompilerError(
                'Field "%s" of union "%s" on line %d has a default value. '
                'Fields of unions cannot have default values. '
                'Please remove the default value for %s.%s from the IDL.'
                % (
                    field.name,
                    union_name,
                    field.lineno,
                    union_name,
                    field.name
                )
            )

    union_dct = {}
    union_dct['type_spec'] = spec
    union_dct['__slots__'] = tuple(field_names)
    union_dct['__init__'] = union_init(union_name, field_names)
    union_dct['__str__'] = union_str(union_name, field_names)
    union_dct['__repr__'] = union_dct['__str__']

    return type(union_name, (base_cls,), union_dct)
