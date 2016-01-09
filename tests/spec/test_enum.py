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

from thriftrw.errors import ThriftCompilerError
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


def test_compile_values_collide(parse):
    enum_ast = parse('enum Foo { A, B, C = 0, D }')
    spec = EnumTypeSpec.compile(enum_ast)

    assert spec.items == {'A': 0, 'B': 1, 'C': 0, 'D': 1}
    assert set(spec.values_to_names[0]) == set(['A', 'C'])
    assert set(spec.values_to_names[1]) == set(['B', 'D'])


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

    assert set(TestEnum.values) == set((1, 2, 3))
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

    assert spec.from_primitive(spec.to_primitive(Enum.A)) == Enum.A
    assert spec.from_primitive(spec.to_primitive(Enum.B)) == Enum.B
    assert spec.from_primitive(spec.to_primitive(Enum.C)) == Enum.C


def test_validate(loads):
    Enum = loads('enum ToWireEnum { A = 2, B = 3, C = -42 }').ToWireEnum
    Enum.type_spec.validate(2)

    with pytest.raises(ValueError):
        Enum.type_spec.validate(4)


def test_enums_are_constants(loads):
    mod = loads('''
        struct Bar {
            1: required Foo foo = Foo.A
        }

        enum Foo {
            A, B, C
        }
    ''')

    Foo = mod.Foo
    Bar = mod.Bar

    assert Bar().foo == Foo.A == 0


@pytest.mark.parametrize('s', [
    '''
        enum X { A = 1, B = 2, C = 4 }
        const X x = 3
    ''',
    '''
        enum X { A = 1, B = 2, C = 4 }
        struct Y { 1: required X x = 3 }
    ''',
])
def test_enum_constant_invalid_default(loads, s):
    with pytest.raises(ThriftCompilerError) as exc_info:
        loads(s)

    assert 'is not a valid value for enum "X"' in str(exc_info)


def test_has_thrift_module(loads):
    module = loads('''
        enum Foo {
            A = 1, B, C
        }
    ''')
    assert module is module.Foo.__thrift_module__


def test_primitive_type_string(loads):
    Answer = loads('''
        enum Answer {
            Yes, No, Unspecified
        } (py.primitiveType = "string")
    ''').Answer

    spec = Answer.type_spec

    assert spec.to_primitive(Answer.Yes) == 'Yes'
    assert spec.to_primitive(Answer.No) == 'No'
    assert spec.to_primitive(Answer.Unspecified) == 'Unspecified'

    for i in [Answer.Yes, Answer.No, Answer.Unspecified]:
        assert spec.from_primitive(spec.to_primitive(i)) == i

    assert spec.to_wire(Answer.Yes) == vi32(0)
    assert spec.to_wire(Answer.No) == vi32(1)
    assert spec.to_wire(Answer.Unspecified) == vi32(2)

    with pytest.raises(ValueError) as exc_info:
        spec.to_primitive(42)
    assert (
        'Enum "Answer" does not define an item with value 42' in str(exc_info)
    )

    with pytest.raises(ValueError) as exc_info:
        spec.from_primitive('Umm')
    assert (
        'Enum "Answer" does not define an item with name "Umm"'
        in str(exc_info)
    )
