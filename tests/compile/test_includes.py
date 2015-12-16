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

import time
import pytest

from thriftrw.loader import Loader
from thriftrw.protocol import BinaryProtocol
from thriftrw.errors import ThriftCompilerError


@pytest.fixture
def loader():
    return Loader(BinaryProtocol(), include_as=True)


def test_simple_include(tmpdir, loader):
    types_source = '''
        struct Item {
            1: required string key
            2: required string value
        }
    '''
    tmpdir.join('types.thrift').write(types_source)

    svc_source = '''
        include "./types.thrift"

        struct BatchGetResponse {
            1: required list<types.Item> items = []
        }

        service ItemStore {
            BatchGetResponse batchGetItems(1: list<string> keys)
        }
    '''
    tmpdir.join('svc.thrift').write(svc_source)

    svc = loader.load(str(tmpdir.join('svc.thrift')))

    # Loading the module we depend on explicitly should give back the same
    # generated module.
    assert svc.types is loader.load(str(tmpdir.join('types.thrift')))
    assert svc.types.__thrift_source__ == types_source
    assert svc.__includes__ == (svc.types,)
    assert svc.__thrift_source__ == svc_source

    item = svc.types.Item(key='foo', value='bar')
    response = svc.BatchGetResponse([item])

    assert svc.types.dumps(item) == bytes(bytearray([
        # 1: 'foo'
        0x0B,
        0x00, 0x01,
        0x00, 0x00, 0x00, 0x03,
        0x66, 0x6f, 0x6f,

        # 2: 'bar'
        0x0B,
        0x00, 0x02,
        0x00, 0x00, 0x00, 0x03,
        0x62, 0x61, 0x72,

        0x00,
    ]))

    svc.dumps(response) == bytes(bytearray([
        # 1: [item]
        0x0F,
        0x00, 0x01,

        # item
        0x0C,
        0x00, 0x00, 0x00, 0x01,

        # 1: 'foo'
        0x0B,
        0x00, 0x01,
        0x00, 0x00, 0x00, 0x03,
        0x66, 0x6f, 0x6f,

        # 2: 'bar'
        0x0B,
        0x00, 0x01,
        0x00, 0x00, 0x00, 0x03,
        0x62, 0x61, 0x72,

        0x00,
    ]))


def test_include_relative(tmpdir, loader):
    tmpdir.join('types/shared.thrift').ensure().write('''
        typedef i64 Timestamp

        exception InternalError {
            1: required string message
        }
    ''')

    tmpdir.join('team/myservice/myservice.thrift').ensure().write('''
        include t "../../types/shared.thrift"

        service Service {
            t.Timestamp getCurrentTime()
                throws (1: t.InternalError internalError)
        }
    ''')

    myservice = loader.load(
        str(tmpdir.join('team/myservice/myservice.thrift'))
    )

    assert myservice.__includes__ == (myservice.t,)

    myservice.Service.getCurrentTime.response(
        success=int(time.time() * 1000)
    )

    myservice.Service.getCurrentTime.response(
        internalError=myservice.t.InternalError('great sadness')
    )

    with pytest.raises(TypeError) as exc_info:
        myservice.Service.getCurrentTime.response(
            success='2015-10-29T15:00:00Z'
        )
    assert 'Cannot serialize' in str(exc_info)

    with pytest.raises(TypeError) as exc_info:
        myservice.Service.getCurrentTime.response(
            internalError=ZeroDivisionError()
        )

    assert 'Cannot serialize' in str(exc_info)


def test_cyclic_includes(tmpdir, loader):
    tmpdir.join('node.thrift').write('''
        include "./value.thrift"

        struct Node {
            1: required string name
            2: required value.Value value
        }
    ''')

    tmpdir.join('value.thrift').write('''
        include "./node.thrift"

        struct Value {
            1: required list<node.Node> nodes
        }
    ''')

    node = loader.load(str(tmpdir.join('node.thrift')))

    assert node.__includes__ == (node.value,)
    assert node.value.__includes__ == (node,)

    assert (
        node.dumps(node.Node('hello', node.value.Value([]))) ==
        bytes(bytearray([

            # 1: 'hello'
            0x0B,
            0x00, 0x01,
            0x00, 0x00, 0x00, 0x05,
            0x68, 0x65, 0x6c, 0x6c, 0x6f,   # 'hello'

            # 2: {1: []}
            0x0C,
            0x00, 0x02,

            # 1: []
            0x0F,
            0x00, 0x01,

            # []
            0x0C,
            0x00, 0x00, 0x00, 0x00,

            0x00,

            0x00,
        ]))
    )


def test_inherit_included_service(tmpdir, loader):
    tmpdir.join('common.thrift').write('''
        service BaseService {
            string serviceName()
            bool healthy()
        }
    ''')

    tmpdir.join('keyvalue.thrift').write('''
        include "./common.thrift"

        service KeyValue extends common.BaseService {
            binary get(1: binary key)
            void put(1: binary key, 2: binary value)
        }
    ''')

    keyvalue = loader.load(str(tmpdir.join('keyvalue.thrift')))

    assert keyvalue.__includes__ == (keyvalue.common,)

    assert issubclass(keyvalue.KeyValue, keyvalue.common.BaseService)

    assert (
        keyvalue.dumps(keyvalue.KeyValue.healthy.response(success=True)) ==
        bytes(bytearray([0x02, 0x00, 0x00, 0x01, 0x00]))
    )


def test_include_constants(tmpdir, loader):
    tmpdir.join('bar.thrift').write('const i32 some_num = 42')

    tmpdir.join('foo.thrift').write('''
        include "./bar.thrift"

        const list<i32> nums = [1, bar.some_num, 2];
    ''')

    foo = loader.load(str(tmpdir.join('foo.thrift')))
    assert foo.nums == [1, 42, 2] == [1, foo.bar.some_num, 2]


def test_include_enums(tmpdir, loader):
    tmpdir.join('foo.thrift').write('''
        enum Role {
            DISABLED = 0,
            USER = 1,
            MOD = 2,
            ADMIN = 3,
        }
    ''')

    tmpdir.join('bar.thrift').write('''
        include "./foo.thrift"

        const foo.Role DEFAULT_ROLE = foo.Role.USER
    ''')

    bar = loader.load(str(tmpdir.join('bar.thrift')))
    assert bar.DEFAULT_ROLE == bar.foo.Role.USER == 1


def test_multi_level_cyclic_import(tmpdir, loader):

    # |- a.thrift
    # |- one/
    #     |- b.thrift
    #     |- c.thrift
    #     |- two/
    #         |- d.thrift

    tmpdir.join('a.thrift').write('''
        include "./one/b.thrift"
        include "./one/c.thrift"
    ''')

    tmpdir.join('one/b.thrift').ensure().write('''
        include "./two/d.thrift"
    ''')

    tmpdir.join('one/c.thrift').ensure().write('''
        include "./two/d.thrift"
    ''')

    tmpdir.join('one/two/d.thrift').ensure().write('''
        include "../../a.thrift"
    ''')

    a = loader.load(str(tmpdir.join('a.thrift')))
    assert (
        a.__includes__ == (a.b, a.c) or
        a.__includes__ == (a.c, a.b)
    )

    assert a.b.d is a.c.d

    assert a.b.__includes__ == (a.b.d,)
    assert a.c.__includes__ == (a.c.d,)

    assert a.b.d.a is a
    assert a.c.d.a is a
    assert a.b.d.__includes__ == (a,)
    assert a.c.d.__includes__ == (a,)


def test_include_as_nested_cyclic_same_name(tmpdir, loader):
    tmpdir.join('a.thrift').write('include t "./b.thrift"')
    tmpdir.join('b.thrift').write('include t "./c.thrift"')
    tmpdir.join('c.thrift').write('include t "./d.thrift"')
    tmpdir.join('d.thrift').write('include t "./a.thrift"')

    a = loader.load(str(tmpdir.join('a.thrift')))
    assert a.t is loader.load(str(tmpdir.join('b.thrift')))
    assert a.t.t is loader.load(str(tmpdir.join('c.thrift')))
    assert a.t.t.t is loader.load(str(tmpdir.join('d.thrift')))
    assert a.t.t.t.t is a

    assert a.__thrift_source__ == 'include t "./b.thrift"'
    assert a.t.__thrift_source__ == 'include t "./c.thrift"'
    assert a.t.t.__thrift_source__ == 'include t "./d.thrift"'
    assert a.t.t.t.__thrift_source__ == 'include t "./a.thrift"'


def test_include_as_disabled(tmpdir):
    loader = Loader()
    tmpdir.join('a.thrift').write('include t "./b.thrift"')
    tmpdir.join('b.thrift').write('typedef string UUID')

    with pytest.raises(ThriftCompilerError) as exc_info:
        loader.load(str(tmpdir.join('a.thrift')))

    assert 'Cannot include "b" as "t"' in str(exc_info)
    assert '"include-as" syntax is currently disabled' in str(exc_info)


@pytest.mark.parametrize('root, data, msgs', [
    (
        # File does not exist
        'foo.thrift',
        [('foo.thrift', 'include "./bar.thrift"')],
        [
            'Cannot include "./bar.thrift"',
            'The file', 'does not exist'
        ]
    ),
    (
        # Two modules in subdirectories with the same name.
        'index.thrift',
        [
            ('foo/shared.thrift', 'typedef string timestamp'),
            ('bar/shared.thrift', 'typedef string UUID'),
            ('index.thrift', '''
                include "./foo/shared.thrift"
                include "./bar/shared.thrift"
            '''),
        ],
        [
            'Cannot include module "shared"',
            'The name is already taken'
        ]
    ),
    (
        # Conflict in include-as name.
        'index.thrift',
        [
            ('foo.thrift', 'typedef i64 timestamp'),
            ('t.thrift', 'typedef string UUID'),
            ('index.thrift', '''
                include "./t.thrift"
                include t "./foo.thrift"
            '''),
        ],
        [
            'Cannot include module "foo" as "t"',
            'The name is already taken',
        ]
    ),
    (
        # Unknown type reference
        'foo.thrift',
        [
            ('foo.thrift', '''
                include "./bar.thrift"

                struct Foo { 1: required bar.Bar b }
            '''),
            ('bar.thrift', ''),
        ],
        ['Unknown type "Bar" referenced']
    ),
    (
        # Unknown service reference
        'foo.thrift',
        [
            ('foo.thrift', '''
                include "./bar.thrift"

                service Foo extends bar.Bar {
                }
            '''),
            ('bar.thrift', 'service NotBar {}'),
        ],
        ['Unknown service "Bar" referenced']
    ),
    (
        # Unknown constant reference
        'foo.thrift',
        [
            ('foo.thrift', '''
                include "./bar.thrift"

                const i32 x = bar.y;
            '''),
            ('bar.thrift', 'const i32 z = 42'),
        ],
        ['Unknown constant "y" referenced']
    ),
    (
        # Bad type reference
        'foo.thrift',
        [('foo.thrift', 'struct Foo { 1: required bar.Bar b }')],
        ['Unknown type "bar.Bar" referenced']
    ),
    (
        # Bad service reference
        'foo.thrift',
        [('foo.thrift', 'service Foo extends bar.Bar {}')],
        ['Unknown service "bar.Bar" referenced']
    ),
    (
        # Bad constant reference
        'foo.thrift',
        [('foo.thrift', 'const i32 x = bar.y')],
        ['Unknown constant "bar.y" referenced']
    ),
    (
        # Include path that doesn't start with '.'
        'foo.thrift',
        [
            ('foo.thrift', 'include "bar.thrift"'),
            ('bar.thrift', 'const i32 x = 42'),
        ],
        [
            'Paths in include statements are relative',
            'must be in the form "./foo.thrift"'
        ]
    ),
])
def test_bad_includes(tmpdir, loader, root, data, msgs):
    for path, contents in data:
        tmpdir.join(path).ensure().write(contents)

    with pytest.raises(ThriftCompilerError) as exc_info:
        loader.load(str(tmpdir.join(root)))

    for msg in msgs:
        assert msg in str(exc_info)


def test_include_disallowed_with_loads(loads):
    with pytest.raises(ThriftCompilerError) as exc_info:
        loads('''
            namespace py foo
            namespace js bar

            include "./foo.thrift"
        ''')

    assert (
        'Includes are not supported when using the "loads()"' in str(exc_info)
    )
