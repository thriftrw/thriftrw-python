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


@pytest.mark.parametrize('expr', [
    'const i32 foo = "hello"',
    'const bool b = 1',
    'const string foo = 42',
    'const binary foo = 42',
    'const list<string> foo = [1, 2, 3]',
    'const list<string> foo = {"foo": "bar"}',
    'const map<string, i32> foo = {"foo": "bar"}',
    'const list<bool> foo = [x]; const i32 x = 42',
])
def test_type_mismatch(expr, loads):
    with pytest.raises(ThriftCompilerError) as exc_info:
        loads(expr)

    assert 'Value for constant' in str(exc_info)
    assert (
        'does not match its type' in str(exc_info) or
        'is not valid' in str(exc_info)
    )


def test_link(loads):
    mod = loads('''
        const list<string> lst = [bar, baz, qux];

        const map<i32, string> mp = {
            1: bar,
            2: baz,
            3: qux
        };

        const i32 foo = 42;
        const i32 foo2 = 0x2a;

        const string baz = bar;
        const string bar = "hello";
        const string qux = "world";

        const bool a = true;
        const bool b = false;

        const Level lo = Level.LOW;
        const Level hi = 2;

        enum Level { LOW, MEDIUM, HIGH }
    ''')

    assert mod.foo == 42
    assert mod.foo2 == 42
    assert mod.bar == 'hello'
    assert mod.baz == 'hello'
    assert mod.qux == 'world'

    assert mod.Level.LOW == mod.lo
    assert mod.Level.HIGH == mod.hi

    assert mod.a
    assert not mod.b

    assert mod.lst == ['hello', 'hello', 'world']
    assert mod.mp == {
        1: 'hello',
        2: 'hello',
        3: 'world',
    }


def test_undefined_constant(loads):
    with pytest.raises(ThriftCompilerError) as exc_info:
        loads('const string baz = bar')

    assert 'Unknown constant "bar"' in str(exc_info)


def test_duplicate_constant(loads):
    with pytest.raises(ThriftCompilerError) as exc_info:
        loads('''
            const i32 foo = 42;
            const string foo = "bar"
        ''')

    assert 'Cannot define constant "foo"' in str(exc_info)
    assert 'name is already taken' in str(exc_info)


def test_invalid_enum(loads):
    with pytest.raises(ThriftCompilerError) as exc_info:
        loads('''
            enum Foo {
                A, B, C
            }

            const Foo foo = 3
        ''')

    assert 'Value for constant "foo" is not valid' in str(exc_info)
