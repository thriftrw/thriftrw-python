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

from thriftrw.compile.exceptions import ThriftCompilerError
from thriftrw.spec.enum import EnumTypeSpec
from thriftrw.idl import Parser

from ..util.value import vi32


@pytest.fixture
def parse():
    """Parser for enum definitions."""
    return Parser(start='enum', silent=True).parse


def test_compile_implicit_values(parse):
    enum_ast = parse('enum ImplicitEnum { A, B, C }')

    spec = EnumTypeSpec.compile(enum_ast)
    assert spec.name == 'ImplicitEnum'
    assert spec.items == {'A': 0, 'B': 1, 'C': 2}


def test_compile_explicit_values(parse):
    enum_ast = parse('enum ExplicitEnum { A = 1, B = 5, C = 3 }')

    spec = EnumTypeSpec.compile(enum_ast)
    assert spec.name == 'ExplicitEnum'
    assert spec.items == {'A': 1, 'B': 5, 'C': 3}


def test_compile_implicit_and_explicit_values(parse):
    enum_ast = parse('enum CombinationEnum { A = 1, B, C = 5, D, E }')

    spec = EnumTypeSpec.compile(enum_ast)
    assert spec.name == 'CombinationEnum'
    assert spec.items == {'A': 1, 'B': 2, 'C': 5, 'D': 6, 'E': 7}


def test_compile_duplicate_names(parse):
    enum_ast = parse('enum DupeEnum { A, B, A }')

    with pytest.raises(ThriftCompilerError) as exc_info:
        EnumTypeSpec.compile(enum_ast)

    assert 'DupeEnum.A' in str(exc_info)
    assert 'has duplicates' in str(exc_info)


def test_compile_values_collide():
    with pytest.raises(ThriftCompilerError) as exc_info:
        EnumTypeSpec(
            'TestEnum',
            {'A': 1, 'B': 5, 'C': 1},
        )

    assert 'Enums items cannot share values' in str(exc_info)


def test_link(loads):
    TestEnum = loads('''
        enum TestEnum {
            A = 1, B, C
        }
    ''').TestEnum

    assert TestEnum.A == 1
    assert TestEnum.B == 2
    assert TestEnum.C == 3

    assert TestEnum.name_of(1) == 'A'
    assert TestEnum.name_of(2) == 'B'
    assert TestEnum.name_of(3) == 'C'
    assert not TestEnum.name_of(4)

    assert set(TestEnum.items) == set(('A', 'B', 'C'))


def test_to_wire(loads):
    Enum = loads('enum ToWireEnum { A = 2, B = 3, C = -42 }').ToWireEnum
    spec = Enum.type_spec

    assert spec.to_wire(Enum.A) == vi32(2)
    assert spec.to_wire(Enum.B) == vi32(3)
    assert spec.to_wire(Enum.C) == vi32(-42)


def test_round_trip(loads):
    Enum = loads('enum RoundTripEnum { A = 2, B = 3, C = -42 }').RoundTripEnum
    spec = Enum.type_spec

    assert spec.from_wire(spec.to_wire(Enum.A)) == Enum.A
    assert spec.from_wire(spec.to_wire(Enum.B)) == Enum.B
    assert spec.from_wire(spec.to_wire(Enum.C)) == Enum.C


def test_enums_are_constants(loads):
    mod = loads('''
        enum Foo {
            A, B, C
        }

        struct Bar {
            1: required Foo foo = Foo.A
        }
    ''')

    Foo = mod.Foo
    Bar = mod.Bar

    assert Bar().foo == Foo.A
