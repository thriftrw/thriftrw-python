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
from thriftrw.errors import ThriftCompilerError
from thriftrw.errors import UnknownExceptionError
from thriftrw.spec.reference import TypeReference
from thriftrw.spec.service import ServiceSpec
from thriftrw.spec.struct import FieldSpec
from thriftrw.idl import Parser
from thriftrw.wire import ttype

from ..util.value import vstruct, vbinary, vmap, vbool


@pytest.fixture
def parse():
    return Parser(start='service', silent=True).parse


def assert_round_trip(instance, value):
    cls = instance.__class__
    spec = cls.type_spec

    assert spec.to_wire(instance) == value
    assert spec.from_wire(value) == instance

    assert spec.from_primitive(spec.to_primitive(instance)) == instance


def test_compile_oneway_with_return_type(parse):
    with pytest.raises(ThriftCompilerError) as exc_info:
        ServiceSpec.compile(parse('''
            service Foo {
                oneway string foo();
            }
        '''))

    assert 'Function "Foo.foo" is oneway' in str(exc_info)
    assert 'It cannot return a value' in str(exc_info)


def test_compile_oneway_with_exceptions(parse):
    with pytest.raises(ThriftCompilerError) as exc_info:
        ServiceSpec.compile(parse('''
            service Foo {
                oneway void foo() throws (1: SomeException exc);
            }
        '''))

    assert 'Function "Foo.foo" is oneway' in str(exc_info)
    assert 'It cannot raise exceptions' in str(exc_info)


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
    assert put_item_spec.result_spec.return_spec is None

    assert get_item_spec.name == 'getItem'
    assert get_item_spec.args_spec.fields == [
        FieldSpec(1, 'key', prim_spec.TextTypeSpec, False),
    ]
    assert get_item_spec.result_spec.fields == [
        FieldSpec(0, 'success', TypeReference('Item', 8), False),
        FieldSpec(1, 'doesNotExist', TypeReference('KeyDoesNotExist', 10),
                  False),
    ]
    assert get_item_spec.result_spec.return_spec == TypeReference('Item', 8)

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

            oneway void clear();
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

    assert KeyValue.clear.spec.oneway
    assert KeyValue.clear.request is not None
    assert KeyValue.clear.response is None

    assert not KeyValue.putItem.spec.oneway
    assert KeyValue.putItem.response.type_spec.return_spec is None
    assert (
        KeyValue.getItem.response.type_spec.return_spec is
        keyvalue.Item.type_spec
    )

    assert_round_trip(
        KeyValue.putItem.request(
            'hello',
            keyvalue.Item({'a': keyvalue.Value(stringValue=u'world')}),
        ),
        vstruct(
            (1, ttype.BINARY, vbinary(b'hello')),
            (2, ttype.STRUCT, vstruct(
                (1, ttype.MAP, vmap(
                    ttype.BINARY, ttype.STRUCT,
                    (
                        vbinary(b'a'),
                        vstruct((1, ttype.BINARY, vbinary(b'world'))),
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
            (1, ttype.STRUCT, vstruct(
                (1, ttype.BINARY, vbinary(b'hello'))
            )),
        )
    )

    assert_round_trip(
        KeyValue.getItem.request('somekey'),
        vstruct((1, ttype.BINARY, vbinary(b'somekey')))
    )

    assert_round_trip(KeyValue.noop.request(), vstruct())
    assert_round_trip(KeyValue.noop.response(), vstruct())

    assert_round_trip(
        KeyValue.healthy.request(),
        vstruct(),
    )

    assert_round_trip(
        KeyValue.healthy.response(success=True),
        vstruct((0, ttype.BOOL, vbool(True))),
    )

    assert keyvalue.dumps(
        KeyValue.healthy.response(success=False)
    ) == b'\x02\x00\x00\x00\x00'

    assert keyvalue.loads(
        KeyValue.healthy.request, b'\x00'
    ) == KeyValue.healthy.request()


def test_fails_on_absent_return_value(loads):
    m = loads('service Foo { i32 foo(); void bar() }')

    # '\x00' is an empty struct.

    assert m.loads(m.Foo.bar.response, b'\x00') == m.Foo.bar.response()

    with pytest.raises(TypeError) as exc_info:
        m.loads(m.Foo.foo.response, b'\x00')

    assert 'did not receive any values' in str(exc_info)


@pytest.mark.parametrize('method, raw, wire_value', [
    ('something', [
        0x0C,        # typeid:1 = struct
        0x7e, 0xff,  # id:2 = 32511
        0x00,        # value = empty struct
        0x00,        # stop
    ], vstruct((32511, ttype.STRUCT, vstruct()))),
    ('nothing', [
        0x0C,        # typeid:1 = struct
        0x01, 0xff,  # id:2 = 511
        0x00,        # value = empty struct
        0x00,        # stop
    ], vstruct((511, ttype.STRUCT, vstruct()))),
], ids=['returns-i32', 'returns-void'])
def test_unrecognized_exception(loads, method, raw, wire_value):
    raw = bytes(bytearray(raw))

    m = loads('''
        exception GreatSadness {
            1: optional string reason
        }

        service S {
            void nothing()
                throws (128: GreatSadness err);

            i32 something()
                throws (32767: GreatSadness err);
        }
    ''')

    with pytest.raises(UnknownExceptionError) as exc_info:
        m.loads(getattr(m.S, method).response, raw)

    assert (
        ('"S_%s_response" received an unrecognized exception' % method)
        in str(exc_info)
    )
    assert exc_info.value.thrift_response == wire_value


def test_args_and_results_know_function_spec(loads):
    m = loads('''
        exception GreatSadness {
            1: optional string reason
        }

        service S {
            oneway void someOneWayFunction(1: string a);

            void functionReturningVoid(1: i32 a, 2: i64 b);

            string functionReturningNonVoid();

            void functionRaisingException() throws (42: GreatSadness err);
        }
    ''')

    assert (
        m.S.someOneWayFunction.spec is
        m.S.someOneWayFunction.request.type_spec.function
    )
    assert m.S.someOneWayFunction.response is None

    assert (
        m.S.functionReturningVoid.spec is
        m.S.functionReturningVoid.request.type_spec.function
    )
    assert (
        m.S.functionReturningVoid.spec is
        m.S.functionReturningVoid.response.type_spec.function
    )

    assert (
        m.S.functionReturningNonVoid.spec is
        m.S.functionReturningNonVoid.request.type_spec.function
    )
    assert (
        m.S.functionReturningNonVoid.spec is
        m.S.functionReturningNonVoid.response.type_spec.function
    )

    assert (
        m.S.functionRaisingException.spec is
        m.S.functionRaisingException.request.type_spec.function
    )
    assert (
        m.S.functionRaisingException.spec is
        m.S.functionRaisingException.response.type_spec.function
    )
