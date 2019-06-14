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

from thriftrw._cython cimport richcompare
from thriftrw.wire.value cimport FieldValue
from .base cimport TypeSpec

from .const import const_value_or_ref
from .spec_mapper import type_spec_or_ref
from ..errors import ThriftCompilerError


cdef class FieldSpec(object):
    """Specification for a single field on a struct.

    .. py:attribute:: id

        Field identifier of this field.

    .. py:attribute:: name

        Name of the field.

    .. py:attribute:: spec

        :py:class:`TypeSpec` for the type of values accepted by this field.

    .. py:attribute:: required

        Whether this field is required or not.

    .. py:attribute:: default_value

        Default value of the field if any. None otherwise.
    """

    def __init__(self, id, name, spec, required, default_value=None):
        self.id = id
        self.name = str(name)
        self.spec = spec
        self.required = required
        self.hashable = False
        self.default_value = default_value
        self.linked = False

    def link(self, scope):
        if not self.linked:
            self.linked = True
            self.spec = self.spec.link(scope)
            self.hashable = self.spec.hashable
            if self.default_value is not None:
                try:
                    self.default_value = self.default_value.link(
                        scope,
                        self.spec
                    ).surface
                except TypeError as e:
                    raise ThriftCompilerError(
                        'Default value for field "%s" does not match '
                        'its type "%s": %s'
                        % (self.name, self.spec.name, e)
                    )
                except ValueError as e:
                    raise ThriftCompilerError(
                        'Default value for field "%s" is not valid: %s'
                        % (self.name, e)
                    )
        return self

    @property
    def ttype_code(FieldSpec self):
        return self.spec.ttype_code

    @classmethod
    def compile(cls, field, struct_name, require_requiredness=True):
        if field.id is None:
            raise ThriftCompilerError(
                'Field "%s" of "%s" does not have an explicit field ID. '
                'Please specify the numeric ID for the field.'
                % (field.name, struct_name)
            )

        required = field.requiredness
        if required is None:
            if require_requiredness:
                raise ThriftCompilerError(
                    'Field "%s" of "%s" on line %d does not explicitly '
                    'specify requiredness. Please specify whether the field '
                    'is optional or required in the IDL.'
                    % (field.name, struct_name, field.lineno)
                )
            else:
                required = False

        # TODO check field ids are valid signed 16-bit integers

        default_value = None
        if field.default is not None:
            default_value = const_value_or_ref(field.default)

        field_type_spec = type_spec_or_ref(field.field_type)
        return cls(
            id=field.id,
            name=field.name,
            spec=field_type_spec,
            required=required,
            default_value=default_value,
        )

    # While FieldSpec has an interface similar to TypeSpec, it's not an actual
    # TypeSpec.

    def to_wire(self, value):
        assert value is not None
        return FieldValue(
            id=self.id,
            ttype=self.spec.ttype_code,
            value=self.spec.to_wire(value),
        )

    def from_wire(self, wire_value):
        assert wire_value is not None
        return self.spec.from_wire(wire_value.value)

    def __str__(self):
        # Field __str__ must reference spec names instead of the specs to
        # avoid an infinite loop in case the field is self-referential.
        return 'FieldSpec(id=%r, name=%r, spec_name=%r)' % (
            self.id, self.name, self.spec.name
        )

    def __repr__(self):
        return str(self)

    def __richcmp__(FieldSpec self, FieldSpec other not None, int op):
        return richcompare(op, [
            (self.id, other.id),
            (self.name, other.name),
            (self.spec, other.spec),
            (self.required, other.required),
        ])
