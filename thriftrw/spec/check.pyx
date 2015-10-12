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


__all__ = ['type_code_matches', 'instanceof_surface']


def type_code_matches(type_spec, wire_value):
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


def instanceof_surface(type_spec, value):
    """Verifies that the value is an instance of the type's surface.

    Raises ``TypeError`` if not.

    :param thriftrw.spec.base.TypeSpec type_spec:
        TypeSpec against which the value is being checked.
    :param value:
        Value being validated.
    """
    instanceof_class(type_spec, type_spec.surface, value)


def instanceof_class(type_spec, cls, value):
    if not isinstance(value, cls):
        raise TypeError(
            'Cannot serialize %r into a "%s".' % (value, type_spec.name)
        )
