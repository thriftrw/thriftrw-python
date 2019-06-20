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

from thriftrw.wire import ttype

from .primitive import TextTypeSpec
from .spec_mapper import type_spec_or_ref
from ..errors import ThriftCompilerError


class ConstValuePrimitive(object):

    __slots__ = ('surface', 'linked', 'hashable')

    def __init__(self, value):
        self.surface = value
        self.linked = False
        self.hashable = True

    def link(self, scope, type_spec):
        if not self.linked:
            self.linked = True
            type_spec.validate(self.surface)
            self.surface = type_spec.from_primitive(
                type_spec.to_primitive(self.surface)
            )
        return self

    def __hash__(self):
        return hash(self.surface)


class ContsValueMap(object):

    __slots__ = ('items', 'linked', 'surface', 'hashable')

    def __init__(self, items):
        self.items = items
        self.linked = False
        self.surface = None
        self.hashable = False

    def link(self, scope, type_spec):
        if type_spec.ttype_code not in (ttype.MAP, ttype.STRUCT):
            raise TypeError('Expected a %s but got a map.' % type_spec.name)

        if self.linked:
            return self

        self.linked = True
        if type_spec.ttype_code == ttype.STRUCT:
            return self._link_struct(scope, type_spec)
        else:
            return self._link_map(scope, type_spec)

    def _link_map(self, scope, type_spec):
        data = {
            k.link(
                scope,
                type_spec.kspec
            ).surface: v.link(scope, type_spec.vspec).surface
            for k, v in self.items.items()
        }

        # Validate it and cast it into whatever the type_spec expects.
        type_spec.validate(data)
        self.surface = type_spec.from_primitive(type_spec.to_primitive(data))
        return self

    def _link_struct(self, scope, type_spec):
        # Resolve keys to strings.
        field_values = {
            k.link(scope, TextTypeSpec).surface: v
            for k, v in self.items.items()
        }
        data = {}

        for field in type_spec.fields:
            attr_name = field.name
            if attr_name in field_values:
                const_value = field_values[attr_name]
                data[attr_name] = const_value.link(scope, field.spec).surface

        self.surface = type_spec.surface(**data)
        return self


class ConstValueList(object):

    __slots__ = ('values', 'linked', 'surface', 'hashable')

    def __init__(self, values):
        self.values = values
        self.linked = False
        self.surface = None
        self.hashable = False

    def link(self, scope, type_spec):
        if type_spec.ttype_code not in (ttype.LIST, ttype.SET):
            raise TypeError('Expected a %s but got a list.' % type_spec.name)
        if not self.linked:
            self.linked = True

            self.surface = [
                v.link(scope, type_spec.vspec).surface for v in self.values
            ]

            # Validate it and cast it into whatever the type_spec expects.
            type_spec.validate(self.surface)
            self.surface = type_spec.from_primitive(
                type_spec.to_primitive(self.surface)
            )
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
    def compile(cls, constant):
        # TODO validate that const.name is a valid python identifier.
        type_spec = type_spec_or_ref(constant.value_type)
        value_spec = const_value_or_ref(constant.value)

        return cls(constant.name, value_spec, type_spec)

    def link(self, scope):
        if not self.linked:
            self.linked = True
            self.type_spec = self.type_spec.link(scope)
            try:
                self.value_spec = self.value_spec.link(scope, self.type_spec)
                value = self.value_spec.surface
                self.type_spec.validate(value)
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

    def visit_primitive(self, constant):
        return ConstValuePrimitive(constant.value)

    def visit_list(self, constant):
        return ConstValueList([self.get(v) for v in constant.values])

    def visit_map(self, constant):
        return ContsValueMap({
            self.get(k): self.get(v) for k, v in constant.pairs.items()
        })

    def visit_reference(self, constant):
        return ConstValueReference(constant.name, constant.lineno)


const_value_or_ref = ConstValueMapper().get
