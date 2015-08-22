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


@pytest.fixture
def parse():
    """Parser for enum definitions."""
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


def test_compile_duplicate_fields(parse):
    struct_ast = parse(
        'struct Foo { 1: required string x; 2: optional i32 x }'
    )

    with pytest.raises(ThriftCompilerError) as exc_info:
        StructTypeSpec.compile(struct_ast)

    assert 'Field "x" of struct "Foo"' in str(exc_info)
    assert 'has duplicates' in str(exc_info)


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


def test_link_all_required(scope):
    spec = StructTypeSpec('ReqStruct', fields=[
        FieldSpec(1, 'x', spec=prim_spec.TextTypeSpec, required=True),
        FieldSpec(2, 'y', spec=prim_spec.I32TypeSpec, required=True),
        FieldSpec(3, 'z', spec=prim_spec.I64TypeSpec, required=True),
    ])
    spec = spec.link(scope)

    ReqStruct = spec.surface
    obj = ReqStruct('hello', 42, 123)
    assert 'hello' == obj.x
    assert 42 == obj.y
    assert 123 == obj.z
