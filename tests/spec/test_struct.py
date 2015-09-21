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
from thriftrw.spec.struct import StructTypeSpec
from thriftrw.spec.struct import FieldSpec
from thriftrw.idl import Parser
from thriftrw.spec import primitive as prim_spec
from thriftrw.spec.reference import TypeReference
from thriftrw.wire.ttype import TType

from ..util.value import vstruct, vbinary, vi64, vi32


@pytest.fixture
def parse():
    return Parser(start='struct', silent=True).parse


def test_compile_missing_field_id(parse):
    struct_ast = parse('struct Foo { required string param }')

    with pytest.raises(ThriftCompilerError) as exc_info:
        StructTypeSpec.compile(struct_ast)

    assert 'Please specify the numeric ID for the field' in str(exc_info)


def test_compile_missing_requiredness(parse):
    struct_ast = parse('struct Foo { 1: string param }')

    with pytest.raises(ThriftCompilerError) as exc_info:
        StructTypeSpec.compile(struct_ast)

    assert (
        'Please specify whether the field is optional or required'
        in str(exc_info)
    )


def test_compile_non_strict_missing_requiredness(parse):
    struct_ast = parse('struct Foo { 1: string param }')

    assert StructTypeSpec.compile(struct_ast, require_requiredness=False)


def test_compile_duplicate_fields(parse):
    struct_ast = parse(
        'struct Foo { 1: required string x; 2: optional i32 x }'
    )

    with pytest.raises(ThriftCompilerError) as exc_info:
        StructTypeSpec.compile(struct_ast)

    assert 'Field "x" of struct "Foo"' in str(exc_info)
    assert 'has duplicates' in str(exc_info)


def test_compile_duplicate_field_ids(parse):
    struct_ast = parse(
        'struct Foo { 1: required string x; 1: optional i32 y; }'
    )

    with pytest.raises(ThriftCompilerError) as exc_info:
        StructTypeSpec.compile(struct_ast)

    assert 'Field ID "1" of struct "Foo"' in str(exc_info)
    assert 'has already been used' in str(exc_info)


def test_compile_primitives(parse):
    struct_ast = parse('''struct PrimitiveStruct {
        1: required string x;
        2: optional i32 y;
        3: required double z;
    }''')

    spec = StructTypeSpec.compile(struct_ast)

    assert spec.name == 'PrimitiveStruct'
    assert spec.fields == [
        FieldSpec(id=1, name='x', spec=prim_spec.TextTypeSpec, required=True),
        FieldSpec(id=2, name='y', spec=prim_spec.I32TypeSpec, required=False),
        FieldSpec(
            id=3, name='z', spec=prim_spec.DoubleTypeSpec, required=True
        ),
    ]


def test_compile_reference(parse):
    struct_ast = parse('''struct RefStruct {
        1: optional string x;
        2: required SomeCustomType y;
        3: optional AnotherCustomType z;
    }''')

    spec = StructTypeSpec.compile(struct_ast)

    assert spec.name == 'RefStruct'
    assert spec.fields == [
        FieldSpec(id=1, name='x', spec=prim_spec.TextTypeSpec, required=False),
        FieldSpec(
            id=2, name='y', spec=TypeReference('SomeCustomType', 3),
            required=True,
        ),
        FieldSpec(
            id=3, name='z', spec=TypeReference('AnotherCustomType', 4),
            required=False,
        ),
    ]


def test_link_simple(scope):
    spec = StructTypeSpec('SimpleStruct', fields=[
        FieldSpec(1, 'a', spec=prim_spec.TextTypeSpec, required=True),
        FieldSpec(2, 'b', spec=prim_spec.BinaryTypeSpec, required=False),
        FieldSpec(3, 'c', spec=prim_spec.I32TypeSpec, required=True),
        FieldSpec(4, 'd', spec=prim_spec.I64TypeSpec, required=False),
    ])
    spec = spec.link(scope)

    SimpleStruct = spec.surface
    assert SimpleStruct.type_spec is spec


def test_load_simple(loads):
    SimpleStruct = loads('''
        struct SimpleStruct {
            1: required string a
            2: optional binary b
            3: required i32 c
            4: optional i64 d
        }
    ''').SimpleStruct

    obj = SimpleStruct('hello', 42)
    assert obj.a == 'hello'
    assert obj.c == 42
    assert None == obj.b == obj.d

    obj = SimpleStruct(c=42, a='hello', b=b'world', d=2)
    assert obj.a == 'hello'
    assert obj.b == b'world'
    assert obj.c == 42
    assert obj.d == 2

    assert SimpleStruct('hello', 42) == SimpleStruct('hello', 42)
    assert SimpleStruct('hello', 42) != SimpleStruct('world', 42)


def test_simple_to_wire(loads):
    ToWireStruct = loads('''struct ToWireStruct {
        1: required string a;
        2: optional binary b
    }''').ToWireStruct
    spec = ToWireStruct.type_spec

    assert spec.to_wire(ToWireStruct('hello', b'world')) == vstruct(
        (1, TType.BINARY, vbinary(b'hello')),
        (2, TType.BINARY, vbinary(b'world')),
    )

    assert spec.to_wire(ToWireStruct('hello')) == vstruct(
        (1, TType.BINARY, vbinary(b'hello'))
    )


def test_required_field_missing(loads):
    X = loads('struct X { 1: required string foo }').X
    spec = X.type_spec

    x = X('foo')
    x.foo = None

    with pytest.raises(TypeError) as exc_info:
        spec.to_wire(x)

    assert 'Field "foo" of "X" is required' in str(exc_info)


def test_empty(loads):
    S = loads('struct S {}').S
    spec = S.type_spec
    assert spec.to_wire(S()) == vstruct()


def test_simple_round_trip(loads):
    RoundTripStruct = loads('''struct RoundTripStruct {
        1: required string a;
        2: optional binary b;
    }''').RoundTripStruct
    spec = RoundTripStruct.type_spec

    assert RoundTripStruct('hello', b'world') == (
        spec.from_wire(spec.to_wire(RoundTripStruct('hello', b'world')))
    )
    assert RoundTripStruct('hello') == (
        spec.from_wire(spec.to_wire(RoundTripStruct('hello')))
    )


def test_default_values(loads):
    Struct = loads('''struct DefaultStruct {
        1: optional i32 optionalField;
        2: optional i64 optionalFieldWithDefault = 42;
        3: required string requiredFieldWithDefault = "";
        4: required string requiredField;
    }''').DefaultStruct
    spec = Struct.type_spec

    # We should end up with this signature:
    #
    # Struct(
    #   requiredField,
    #   optionalField,
    #   optionalFieldWithDefault,
    #   requiredFieldWithDefault,
    # )
    #

    assert spec.to_wire(Struct('hello')) == vstruct(
        (2, TType.I64, vi64(42)),
        (3, TType.BINARY, vbinary(b'')),
        (4, TType.BINARY, vbinary(b'hello')),
    )

    assert spec.to_wire(Struct('hello', 10, 100, u'world')) == vstruct(
        (1, TType.I32, vi32(10)),
        (2, TType.I64, vi64(100)),
        (3, TType.BINARY, vbinary(b'world')),
        (4, TType.BINARY, vbinary(b'hello')),
    )


def test_constructor_behavior(loads):
    Struct = loads('''struct ConstructorStruct {
        1: optional i32 optionalField;
        2: optional i64 optionalFieldWithDefault = 42;
        3: required binary requiredFieldWithDefault = "";
        4: required string requiredField;
    }''').ConstructorStruct

    with pytest.raises(TypeError) as exc_info:
        Struct()
    assert 'takes at least 2 arguments (1 given)' in str(exc_info)

    with pytest.raises(TypeError) as exc_info:
        Struct(1, 2, 3, 4, 5)
    assert 'at most 5 arguments (6 given)' in str(exc_info)

    with pytest.raises(TypeError) as exc_info:
        Struct('hello', requiredField='world')
    assert 'multiple values for argument "requiredField"' in str(exc_info)

    with pytest.raises(TypeError) as exc_info:
        Struct('hello', unknown='world')
    assert 'unexpected keyword argument "unknown"' in str(exc_info)

    with pytest.raises(ValueError) as exc_info:
        Struct(optionalField=10)
    assert 'require non-None values' in str(exc_info)


def test_self_referential(loads):
    Cons = loads('''struct Cons {
        1: required i32 value
        2: optional Cons next
    }''').Cons
    spec = Cons.type_spec

    c = Cons(1, Cons(2, Cons(3, Cons(4, Cons(5)))))

    assert spec.to_wire(c) == vstruct(
        (1, TType.I32, vi32(1)),
        (2, TType.STRUCT, vstruct(
            (1, TType.I32, vi32(2)),
            (2, TType.STRUCT, vstruct(
                (1, TType.I32, vi32(3)),
                (2, TType.STRUCT, vstruct(
                    (1, TType.I32, vi32(4)),
                    (2, TType.STRUCT, vstruct(
                        (1, TType.I32, vi32(5)),
                    )),
                )),
            )),
        )),
    )

    assert spec.from_wire(spec.to_wire(c)) == c
