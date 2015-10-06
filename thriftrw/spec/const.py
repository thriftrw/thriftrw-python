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

import six

from thriftrw.compile.exceptions import ThriftCompilerError

from .spec_mapper import type_spec_or_ref


class ConstValuePrimitive(object):

    __slots__ = ('surface',)

    def __init__(self, value):
        self.surface = value

    def link(self, scope, type_spec):
        if (
            type_spec.name == 'binary' and
            isinstance(self.surface, six.string_types)
        ):
            self.surface = self.surface.encode('utf-8')

        return self


class ContsValueMap(object):

    __slots__ = ('items', 'linked', 'surface')

    def __init__(self, items):
        self.items = items
        self.linked = False
        self.surface = None

    def link(self, scope, type_spec):
        if not self.linked:
            self.linked = True
            self.surface = {
                k.link(
                    scope,
                    type_spec
                ).surface: v.link(scope, type_spec).surface
                for k, v in self.items.items()
            }
        return self


class ConstValueList(object):

    __slots__ = ('values', 'linked', 'surface')

    def __init__(self, values):
        self.values = values
        self.linked = False
        self.surface = None

    def link(self, scope, type_spec):
        if not self.linked:
            self.linked = True
            self.surface = [
                v.link(scope, type_spec).surface for v in self.values
            ]
        return self


class ConstValueReference(object):

    __slots__ = ('name', 'lineno')

    def __init__(self, name, lineno):
        self.name = name
        self.lineno = lineno

    def link(self, scope, type_spec):
        return scope.resolve_const_spec(self.name, self.lineno)

    def __str__(self):
        return 'ConstValueReference(name=%s, lineno=%d)' % (
            self.name, self.lineno
        )

    __repr__ = __str__


class ConstSpec(object):
    """Spec for a constant value defined in the Thrift file.

    The surface for a ConstSpec is the value defined in the Thrift file.

    The following,::

        const list<i32> foo = [1, 2, 3]

    Roughly translates to,

    .. code-block:: python

        foo = [1, 2, 3]

    In the generated module.
    """

    __slots__ = (
        'name', 'type_spec', 'value_spec', 'linked', 'surface', 'save'
    )

    def __init__(self, name, value_spec, type_spec, save=None):
        """
        :param name:
            Name of the constant.
        :param value_spec:
            spec of the constant value
        :param type_spec:
            TypeSpec for the type of the value. The value will be validated
            against this spec.
        :param save:
            Whether the constant's surface should be exposed in the generated
            module. Defaults to True.
        """

        #: Name of the constant.
        self.name = name

        self.value_spec = value_spec
        self.type_spec = type_spec

        self.linked = False
        self.surface = None

        if save is None:
            save = True
        self.save = save

    @classmethod
    def compile(cls, const):
        # TODO validate that const.name is a valid python identifier.
        type_spec = type_spec_or_ref(const.value_type)
        value_spec = const_value_or_ref(const.value)

        return cls(const.name, value_spec, type_spec)

    def link(self, scope):
        if not self.linked:
            self.linked = True
            self.type_spec = self.type_spec.link(scope)
            self.value_spec = self.value_spec.link(scope, self.type_spec)
            value = self.value_spec.surface
            try:
                self.type_spec.to_wire(value)
            except TypeError as e:
                raise ThriftCompilerError(
                    'Value for constant "%s" does not match its type "%s": %s'
                    % (self.name, self.type_spec.name, e)
                )
            except ValueError as e:
                raise ThriftCompilerError(
                    'Value for constant "%s" is not valid: %s'
                    % (self.name, e)
                )
            self.surface = value

        return self


class ConstValueMapper(object):
    """Resolves constant values."""

    __slots__ = ()

    def get(self, const_value):
        return const_value.apply(self)

    def visit_primitive(self, const):
        return ConstValuePrimitive(const.value)

    def visit_list(self, const):
        return ConstValueList([self.get(v) for v in const.values])

    def visit_map(self, const):
        return ContsValueMap({
            self.get(k): self.get(v) for k, v in const.pairs.items()
        })

    def visit_reference(self, const):
        return ConstValueReference(const.name, const.lineno)


const_value_or_ref = ConstValueMapper().get
