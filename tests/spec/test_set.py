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

import pytest

from thriftrw.idl import Parser
from thriftrw.spec import primitive as prim_spec
from thriftrw.spec.set import SetTypeSpec
from thriftrw.spec.typedef import TypedefTypeSpec
from thriftrw.spec.spec_mapper import type_spec_or_ref
from thriftrw.wire.ttype import TType

from ..util.value import vbinary, vset


@pytest.fixture
def parse():
    return Parser(start='set_type', silent=True).parse


def test_mapper(parse):
    ast = parse('set<binary>')
    spec = type_spec_or_ref(ast)
    assert spec == SetTypeSpec(prim_spec.BinaryTypeSpec)


def test_link(parse, scope):
    ast = parse('set<Foo>')
    spec = type_spec_or_ref(ast)

    scope.add_type_spec(
        'Foo', TypedefTypeSpec('Foo', prim_spec.TextTypeSpec), 1
    )

    spec = spec.link(scope)
    assert spec.vspec == prim_spec.TextTypeSpec

    value = set([u'foo', u'bar'])
    assert (
        spec.to_wire(value) == vset(
            TType.BINARY, vbinary(b'foo'), vbinary(b'bar')
        )
    ) or (
        spec.to_wire(value) == vset(
            TType.BINARY, vbinary(b'bar'), vbinary(b'foo')
        )
    )
    assert value == spec.from_wire(spec.to_wire(value))


def test_validate():
    spec = SetTypeSpec(prim_spec.TextTypeSpec)

    spec.validate(set(['a']))

    with pytest.raises(TypeError):
        spec.validate(set([1]))

    with pytest.raises(TypeError):
        spec.validate(1)
