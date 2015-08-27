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

from thriftrw.spec import primitive as prim_spec
from thriftrw.compile.exceptions import ThriftCompilerError
from thriftrw.spec.reference import TypeReference
from thriftrw.spec.service import ServiceSpec
from thriftrw.spec.struct import FieldSpec
from thriftrw.idl import Parser
from thriftrw.wire.ttype import TType

from ..util.value import vstruct, vbinary, vmap, vbool


@pytest.fixture
def parse():
    return Parser(start='service', silent=True).parse


def to_wire(s):
    return s.__class__.type_spec.to_wire(s)


def from_wire(t, s):
    return t.type_spec.from_wire(s)


def test_compile_oneway_function(parse):
    with pytest.raises(ThriftCompilerError) as exc_info:
        ServiceSpec.compile(parse('''
            service Foo { oneway void bar(); }
        '''))

    assert 'Oneway functions are not supported' in str(exc_info)


def test_compile_dupe_func(parse):
    with pytest.raises(ThriftCompilerError) as exc_info:
        ServiceSpec.compile(parse('''
            service Foo {
                void foo();
                i32 foo();
            }
        '''))

    assert 'Function "Foo.foo" cannot be defined' in str(exc_info)
    assert 'name is already taken' in str(exc_info)


def test_dupe_service(loads):
    with pytest.raises(ThriftCompilerError) as exc_info:
        loads('''
            service Foo { }
            service Foo { }
        ''')

    assert 'Cannot define service "Foo"' in str(exc_info)
    assert 'name is already taken' in str(exc_info)


def test_compile(parse):
    spec = ServiceSpec.compile(parse('''
        service KeyValue extends BaseService {
            void putItem(
                1: string key,
                2: Item item
            ) throws (1: ItemAlreadyExists alreadyExists);

            Item getItem(
                1: string key
            ) throws (1: KeyDoesNotExist doesNotExist);

            bool healthy();

            // Does not accept or return anything
            void noop();
        }
    '''))

    assert spec.name == 'KeyValue'
    assert spec.parent == 'BaseService'

    put_item_spec = spec.functions[0]
    get_item_spec = spec.functions[1]
    healthy_spec = spec.functions[2]
    noop_spec = spec.functions[3]

    assert put_item_spec.name == 'putItem'
    assert put_item_spec.args_spec.fields == [
        FieldSpec(1, 'key', prim_spec.TextTypeSpec, False),
        FieldSpec(2, 'item', TypeReference('Item', 5), False),
    ]
    assert put_item_spec.result_spec.fields == [
        FieldSpec(1, 'alreadyExists', TypeReference('ItemAlreadyExists', 6),
                  False),
    ]

    assert get_item_spec.name == 'getItem'
    assert get_item_spec.args_spec.fields == [
        FieldSpec(1, 'key', prim_spec.TextTypeSpec, False),
    ]
    assert get_item_spec.result_spec.fields == [
        FieldSpec(0, 'success', TypeReference('Item', 8), False),
        FieldSpec(1, 'doesNotExist', TypeReference('KeyDoesNotExist', 10),
                  False),
    ]

    assert healthy_spec.name == 'healthy'
    assert healthy_spec.args_spec.fields == []
    assert healthy_spec.result_spec.fields == [
        FieldSpec(0, 'success', prim_spec.BoolTypeSpec, False)
    ]

    assert noop_spec.name == 'noop'
    assert noop_spec.args_spec.fields == []
    assert noop_spec.result_spec.fields == []


def test_link_unknown_parent(loads):
    with pytest.raises(ThriftCompilerError) as exc_info:
        loads('service A extends B {}')

    assert 'Service "A" inherits from unknown service "B"' in str(exc_info)


def test_load(loads):
    keyvalue = loads('''
        service KeyValue extends BaseService {
            void putItem(
                1: string key,
                2: Item item,
            ) throws (1: ItemAlreadyExists alreadyExists);

            Item getItem(
                1: string key,
            ) throws (1: KeyDoesNotExist doesNotExist);
        }

        struct Item {
            1: required map<string, Value> attributes
        }

        union Value {
            1: string stringValue
            2: i32 intValue
            3: list<Value> listValue
        }

        exception ItemAlreadyExists { 1: required string message }
        exception KeyDoesNotExist   { 1: required string message }

        service BaseService {
            bool healthy()

            /* doesn't accept or return anything */
            void noop();
        }
    ''')
    assert (
        (keyvalue.KeyValue, keyvalue.BaseService) == keyvalue.services or
        (keyvalue.BaseService, keyvalue.KeyValue) == keyvalue.services
    )

    KeyValue = keyvalue.KeyValue

    assert_round_trip(
        KeyValue.putItem.request(
            'hello',
            keyvalue.Item({'a': keyvalue.Value(stringValue=u'world')}),
        ),
        vstruct(
            (1, TType.BINARY, vbinary(b'hello')),
            (2, TType.STRUCT, vstruct(
                (1, TType.MAP, vmap(
                    TType.BINARY, TType.STRUCT,
                    (
                        vbinary(b'a'),
                        vstruct((1, TType.BINARY, vbinary(b'world'))),
                    )
                )),
            )),
        ),
    )

    assert_round_trip(KeyValue.putItem.response(), vstruct())

    assert_round_trip(
        KeyValue.putItem.response(
            alreadyExists=keyvalue.ItemAlreadyExists('hello')
        ),
        vstruct(
            (1, TType.STRUCT, vstruct(
                (1, TType.BINARY, vbinary(b'hello'))
            )),
        )
    )

    assert_round_trip(
        KeyValue.getItem.request('somekey'),
        vstruct((1, TType.BINARY, vbinary(b'somekey')))
    )

    assert_round_trip(KeyValue.noop.request(), vstruct())
    assert_round_trip(KeyValue.noop.response(), vstruct())

    assert_round_trip(
        KeyValue.healthy.request(),
        vstruct(),
    )

    assert_round_trip(
        KeyValue.healthy.response(success=True),
        vstruct((0, TType.BOOL, vbool(True))),
    )

    assert keyvalue.dumps(
        KeyValue.healthy.response(success=False)
    ) == b'\x02\x00\x00\x00\x00'

    assert keyvalue.loads(
        KeyValue.healthy.request, b'\x00'
    ) == KeyValue.healthy.request()


def assert_round_trip(instance, value):
    assert to_wire(instance) == value
    assert from_wire(instance.__class__, value) == instance
