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

from thriftrw.wire cimport ttype
from thriftrw.wire.value cimport Value
from thriftrw._cython cimport richcompare
from thriftrw.wire.value cimport StructValue
from .base cimport TypeSpec
from .field cimport FieldSpec
from . cimport check

from . import common
from ..errors import ThriftCompilerError

__all__ = ['StructTypeSpec', 'FieldSpec']


cdef class StructTypeSpec(TypeSpec):
    """A struct is a collection of named fields.

    .. py:attribute:: name

        Name of the struct.

    .. py:attribute:: fields

        Collection of :py:class:`FieldSpec` objects representing the fields of
        this struct.

    The surface for struct types is a class with the following:

    .. py:attribute:: type_spec

        :py:class:`StructTypeSpec` for the type.

    .. py:method:: __init__(self, *args, **kwargs)

        Accepts all fields of the struct as arguments. Required arguments are
        placed first and may be specified as positional arguments (in the same
        order as they appear in the IDL). Optional arguments and required
        arguments come next. A TypeError will be raised if the required
        arguments for the struct are not filled with non-None values.

    .. py:method:: to_primitive(self)

        Converts the struct into a dictionary mapping field names to primitive
        representation of field values.

        Only the following types are used in primitive representations:
        ``bool``, ``bytes``, ``float``, ``str`` (``unicode`` in Python < 3),
        ``int``, ``long``, ``dict``, ``list``.

        .. versionadded:: 0.4

    .. py:classmethod:: from_primitive(cls, value)

        Converts a dictionary holding a primitive representation of a value of
        this type (as returned by ``to_primitive``) into an instance of this
        class.

        .. versionadded:: 0.4

    And obvious definitions of ``__str__`` and ``__eq__``.

    Given the definition,::

        struct User {
            1: required string name
            2: optional string email
            3: required bool isActive = true
        }

    A class roughly equivalent to the following is generated,

    .. code-block:: python

        class User(object):

            __slots__ = ('name', 'email', 'isActive')

            type_spec = # ...

            def __init__(name, email=None, isActive=True):
                # ...
    """

    ttype_code = ttype.STRUCT

    def __init__(self, name, fields, base_cls=None):
        """Initialize a new StructTypeSpec.

        :param str name:
            Name of the Struct.
        :param fields:
            Collection of :py:class:`FieldSpec` objects.
        :param base_cls:
            Base class to use for generates classes. Defaults to ``object``.
        """

        self.name = unicode(name)
        self.fields = fields
        self.linked = False
        self.surface = None
        self.base_cls = base_cls or object

    cpdef TypeSpec link(self, scope):
        if not self.linked:
            self.linked = True
            self.fields = [field.link(scope) for field in self.fields]
            self.surface = struct_cls(self, scope)
        return self

    @classmethod
    def compile(cls, struct, require_requiredness=True):
        fields = []
        ids = set()
        names = set()
        for field in struct.fields:
            if field.name in names:
                raise ThriftCompilerError(
                    'Field "%s" of struct "%s" on line %d has duplicates.' %
                    (field.name, struct.name, field.lineno)
                )
            names.add(field.name)

            if field.id in ids:
                raise ThriftCompilerError(
                    'Field ID "%d" of struct "%s" on line %d '
                    'has already been used.' % (
                        field.id, struct.name, field.lineno
                    )
                )
            ids.add(field.id)
            fields.append(FieldSpec.compile(
                field=field,
                struct_name=struct.name,
                require_requiredness=require_requiredness,
            ))
        return cls(struct.name, fields)

    cpdef Value to_wire(self, object struct):
        fields = []

        for field in self.fields:
            value = getattr(struct, field.name)
            if value is None:
                continue
            fields.append(field.to_wire(value))

        return StructValue(fields)

    cpdef object to_primitive(self, object struct):
        prim = {}

        for field in self.fields:
            value = getattr(struct, field.name)
            if value is None:
                continue

            prim[field.name] = field.spec.to_primitive(value)
        return prim

    cpdef object from_wire(self, Value wire_value):
        check.type_code_matches(self, wire_value)
        kwargs = {}
        for field in self.fields:
            field_value = wire_value.get(field.id, field.ttype_code)
            if field_value is None:
                continue
            kwargs[field.name] = field.from_wire(field_value)

        return self.surface(**kwargs)

    cpdef object from_primitive(self, object prim_value):
        kwargs = {}

        for field in self.fields:
            field_value = prim_value.get(field.name)
            if field_value is None:
                continue
            kwargs[field.name] = field.spec.from_primitive(field_value)

        return self.surface(**kwargs)

    cpdef void validate(self, object instance) except *:
        check.instanceof_surface(self, instance)

        for field in self.fields:
            field_value = getattr(instance, field.name)
            if field_value is None:
                if field.required:
                    raise TypeError(
                        'Field "%s" of "%s" is required. It cannot be None.'
                        % (field.name, self.name)
                    )
                else:
                    continue
            field.spec.validate(field_value)

    def __str__(self):
        return '%s(name=%r, fields=%r)' % (
            self.__class__.__name__, self.name, self.fields
        )

    def __repr__(self):
        return str(self)

    def __richcmp__(StructTypeSpec self, StructTypeSpec other not None, int op):
        return richcompare(op, [
            (self.name, other.name),
            (self.fields, other.fields),
            (self.base_cls, other.base_cls),
        ])


def struct_init(cls_name, field_names, field_defaults, base_cls, validate):
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
        base_cls.__init__(self)

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
                    '%s() got multiple values for argument "%s"'
                    % (cls_name, name)
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

        if kwargs:
            # Too many kwargs given.
            for name in kwargs:
                raise TypeError(
                    '%s() got an unexpected keyword argument "%s"'
                    % (cls_name, name)
                )

        # If anything was left unassigned, blow up.
        if unassigned:
            raise ValueError(
                'Field(s) %r require non-None values.' % list(unassigned)
            )

        # TODO Instead of validating here, validation should be done as values
        # are assigned.
        validate(self)

    # TODO reasonable docstring
    return __init__


def struct_docstring(cls_name, required_fields, optional_fields):
    """Generates a docstring for generated structs."""
    required_section = ''
    if required_fields:
        required_section = '\n'.join(
            [''] +
            ['\nThe following arguments are required:\n'] +
            ['-   %s' % name for name in required_fields]
        )

    optional_section = ''
    if optional_fields:
        optional_section = '\n'.join(
            [''] +
            ['\nThe following arguments are optional:\n'] +
            ['-   %s (default: %s)' % pair
             for pair in optional_fields.items()]
        )

    param_list = (
        list(required_fields) +
        ['%s=None' % name for name in optional_fields.keys()]
    )

    header = '%s(%s)' % (cls_name, ', '.join(param_list))

    return header + required_section + optional_section


def struct_cls(struct_spec, scope):
    """Generate a class for a struct.

    The generated class has the following attributes:

    :param StructTypeSpec struct_spec:
        Type specification of the struct.
    :param thriftrw.compile.Scope scope:
        The compilation scope
    """
    slots = set()

    required_fields = []
    optional_fields = []
    field_defaults = []

    for field in struct_spec.fields:
        slots.add(field.name)

        default = None
        if field.default_value is not None:
            default = field.default_value

        if field.required and default is None:
            # required fields that have default values are optional as far as
            # the constructor is concerned.
            required_fields.append(field.name)
        else:
            optional_fields.append(field.name)
            field_defaults.append(default)

    field_names = required_fields + optional_fields

    struct_dct = {}
    struct_dct['type_spec'] = struct_spec
    struct_dct['to_primitive'] = common.to_primitive_method(struct_spec)
    struct_dct['from_primitive'] = common.from_primitive_classmethod()
    struct_dct['__thrift_module__'] = scope.module
    struct_dct['__slots__'] = tuple(slots)
    struct_dct['__init__'] = struct_init(
        struct_spec.name,
        field_names,
        field_defaults,
        struct_spec.base_cls,
        struct_spec.validate,
    )
    struct_dct['__str__'] = common.fields_str(struct_spec.name, field_names)
    struct_dct['__repr__'] = struct_dct['__str__']
    struct_dct['__eq__'] = common.fields_eq(set(field_names))
    struct_dct['__doc__'] = struct_docstring(
        struct_spec.name,
        required_fields,
        dict(zip(optional_fields, field_defaults)),
    )

    # TODO generate a reasonable docstring for the class too.

    return type(str(struct_spec.name), (struct_spec.base_cls,), struct_dct)
