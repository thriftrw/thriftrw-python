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

from .base cimport TypeSpec

from thriftrw.wire.value cimport Value

__all__ = ['type_code_matches', 'instanceof_surface']


cpdef type_code_matches(TypeSpec type_spec, Value wire_value):
    """Verifies that the ttype_code for the TypeSpec and the Value matches.

    Raises ``ValueError`` if not.

    :param thriftrw.spec.base.TypeSpec type_spec:
        TypeSpec against which the value is being checked.
    :param thriftrw.idl.Value wire_value:
        Wire value being checked.
    """
    if type_spec.ttype_code != wire_value.ttype_code:
        raise ValueError(
            'Cannot read a "%s" (type %d) from %r (type %d)' %
            (type_spec.name, type_spec.ttype_code, wire_value,
             wire_value.ttype_code)
        )


cpdef instanceof_surface(TypeSpec type_spec, object value):
    """Verifies that the value is an instance of the type's surface.

    Raises ``TypeError`` if not.

    :param thriftrw.spec.base.TypeSpec type_spec:
        TypeSpec against which the value is being checked.
    :param value:
        Value being validated.
    """
    instanceof_class(type_spec, type_spec.surface, value)


cpdef instanceof_class(TypeSpec type_spec, cls, object value):
    if not isinstance(value, cls):
        raise TypeError(
            'Cannot serialize %r into a "%s".' % (value, type_spec.name)
        )

cpdef isiterable(TypeSpec type_spec, object value):
    """Checks if the given value is iterable."""
    if not hasattr(value, '__iter__'):
        raise TypeError(
            'Cannot serialize %r into a "%s".' % (value, type_spec.name)
        )

cpdef ismapping(TypeSpec type_spec, object value):
    """Checks if the given value is iterable."""
    if not hasattr(value, '__getitem__') or not hasattr(value, 'items'):
        raise TypeError(
            'Cannot serialize %r into a "%s".' % (value, type_spec.name)
        )
