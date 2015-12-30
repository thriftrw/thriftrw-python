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
from thriftrw.spec.union import UnionTypeSpec
from thriftrw.spec.struct import FieldSpec
from thriftrw.spec.reference import TypeReference
from thriftrw.errors import ThriftCompilerError
from thriftrw.spec import primitive as prim_spec
from thriftrw.spec.list import ListTypeSpec
from thriftrw.wire import ttype

from ..util.value import vstruct, vbinary, vlist, vi32


@pytest.fixture
def parse():
    return Parser(start='union', silent=True).parse


def test_compile_without_field_id(parse):
    with pytest.raises(ThriftCompilerError) as exc_info:
        UnionTypeSpec.compile(parse('union Primitive { string foo }'))

    assert 'Please specify the numeric ID for the field' in str(exc_info)


def test_compile_with_optional_or_required(parse):
    spec = UnionTypeSpec.compile(
        parse('union Foo { 1: optional string bar }')
    )
    assert not spec.fields[0].required

    with pytest.raises(ThriftCompilerError) as exc_info:
        UnionTypeSpec.compile(parse('union Foo { 1: required string bar }'))

    assert 'Field "bar" of union "Foo"' in str(exc_info)
    assert 'is "required".' in str(exc_info)


def test_compile_with_default_value(parse):
    with pytest.raises(ThriftCompilerError) as exc_info:
        UnionTypeSpec.compile(parse('union Foo { 1: string bar = "baz" }'))

    assert 'Field "bar" of union "Foo"' in str(exc_info)
    assert 'has a default value' in str(exc_info)


def test_compile_with_duplicate_field_ids(parse):
    with pytest.raises(ThriftCompilerError) as exc_info:
        UnionTypeSpec.compile(
            parse('union Foo { 1: string bar; 1: i32 baz }')
        )
    assert 'Field ID "1" of union "Foo"' in str(exc_info)
    assert 'has already been used' in str(exc_info)


def test_compile_with_duplicate_names(parse):
    with pytest.raises(ThriftCompilerError) as exc_info:
        UnionTypeSpec.compile(
            parse('union Foo { 1: string bar; 2: i32 bar }')
        )

    assert 'Field "bar" of union "Foo"' in str(exc_info)
    assert 'has duplicates' in str(exc_info)


def test_compile(parse):
    spec = UnionTypeSpec.compile(parse(
        '''union Foo {
            1: binary b
            2: string s
            3: i32 i
            4: list<Foo> l
        }'''
    ))

    assert spec.name == 'Foo'
    assert spec.fields == [
        FieldSpec(id=1, name='b', spec=prim_spec.BinaryTypeSpec,
                  required=False),
        FieldSpec(id=2, name='s', spec=prim_spec.TextTypeSpec,
                  required=False),
        FieldSpec(id=3, name='i', spec=prim_spec.I32TypeSpec,
                  required=False),
        FieldSpec(id=4, name='l', required=False,
                  spec=ListTypeSpec(TypeReference('Foo', 5))),
    ]


def test_load_empty(loads):
    Foo = loads('union Foo {}').Foo
    spec = Foo.type_spec

    assert spec.to_wire(Foo()) == vstruct()
    assert Foo().to_primitive() == {}
    assert Foo.from_primitive({}) == Foo()


def test_load(loads):
    Foo = loads('''union Foo {
        1: binary b
        2: optional string s
        3: optional i32 i
        4: list<Foo> l
    }''').Foo
    spec = Foo.type_spec

    bfoo = Foo(b=b'foo')
    sfoo = Foo(s='bar')
    ifoo = Foo(i=42)
    lfoo = Foo(l=[bfoo, sfoo, ifoo])

    cases = [
        (
            bfoo,
            vstruct((1, ttype.BINARY, vbinary(b'foo'))),
            {'b': b'foo'}
        ),
        (
            sfoo,
            vstruct((2, ttype.BINARY, vbinary(b'bar'))),
            {'s': u'bar'},
        ),
        (
            ifoo,
            vstruct((3, ttype.I32, vi32(42))),
            {'i': 42},
        ),
        (
            lfoo,
            vstruct(
                (4, ttype.LIST, vlist(
                    ttype.STRUCT,
                    vstruct((1, ttype.BINARY, vbinary(b'foo'))),
                    vstruct((2, ttype.BINARY, vbinary(b'bar'))),
                    vstruct((3, ttype.I32, vi32(42))),
                ))
            ),
            {'l': [
                {'b': b'foo'},
                {'s': u'bar'},
                {'i': 42},
            ]},
        )
    ]

    for value, wire_value, prim_value in cases:
        assert spec.to_wire(value) == wire_value
        assert spec.from_wire(wire_value) == value

        assert value.to_primitive() == prim_value
        assert Foo.from_primitive(prim_value) == value


def test_constructor(loads):
    Foo = loads('''union Foo {
        1: binary b
        2: string s
        3: i32 i
    }''').Foo

    with pytest.raises(TypeError) as exc_info:
        Foo()
    assert 'Exactly one non-None value is required' in str(exc_info)

    with pytest.raises(TypeError) as exc_info:
        Foo(unknown=42)
    assert 'unexpected keyword argument "unknown"' in str(exc_info)

    with pytest.raises(TypeError) as exc_info:
        Foo(42)
    assert 'does not accept any positional arguments' in str(exc_info)

    with pytest.raises(TypeError) as exc_info:
        Foo(s='foo', i=42)
    assert 'received multiple values' in str(exc_info)


def test_validate(loads):
    Foo = loads('''union Foo {
        1: string s
        2: i32 i
    }''').Foo

    Foo.type_spec.validate(Foo(s='a'))

    Foo.type_spec.validate(Foo(i=1))

    with pytest.raises(TypeError):
        Foo.type_spec.validate(Foo(i='a'))

    with pytest.raises(TypeError):
        Foo.type_spec.validate(Foo(s=1))


def test_has_thrift_module(loads):
    module = loads('''union Foo {
        1: binary b
        2: string s
    }''')
    assert module is module.Foo.__thrift_module__
