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
from thriftrw.spec.map import MapTypeSpec
from thriftrw.spec.typedef import TypedefTypeSpec
from thriftrw.spec.spec_mapper import type_spec_or_ref
from thriftrw.wire.ttype import TType

from ..util.value import vi32, vmap, vbinary


@pytest.fixture
def parse():
    return Parser(start='map_type', silent=True).parse


def test_mapper(parse):
    ast = parse('map<string, i32>')
    spec = type_spec_or_ref(ast)
    assert spec == MapTypeSpec(prim_spec.TextTypeSpec, prim_spec.I32TypeSpec)


def test_link(parse, scope):
    ast = parse('map<string, Foo>')
    spec = type_spec_or_ref(ast)

    scope.add_type_spec(
        'Foo', TypedefTypeSpec('Foo', prim_spec.I32TypeSpec), 1
    )

    spec = spec.link(scope)
    assert spec.vspec == prim_spec.I32TypeSpec

    value = {u'foo': 1, u'bar': 2}
    assert (
        spec.to_wire(value) == vmap(
            TType.BINARY, TType.I32,
            (vbinary(b'foo'), vi32(1)),
            (vbinary(b'bar'), vi32(2)),
        )
    ) or (
        spec.to_wire(value) == vmap(
            TType.BINARY, TType.I32,
            (vbinary(b'bar'), vi32(2)),
            (vbinary(b'foo'), vi32(1)),
        )
    )
    assert value == spec.from_wire(spec.to_wire(value))
