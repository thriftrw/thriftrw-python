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
from functools import partial

from thriftrw.idl import Parser
from thriftrw.protocol import BinaryProtocol
from thriftrw.compile import Compiler
from thriftrw.compile.exceptions import ThriftCompilerError


@pytest.fixture
def parse():
    return Parser().parse


@pytest.fixture
def compile(request):
    return partial(Compiler(BinaryProtocol()).compile, request.node.name)


@pytest.fixture
def loads(parse, compile):
    return (lambda s: compile(parse(s)))


def test_include_disallowed(loads):
    with pytest.raises(ThriftCompilerError) as exc_info:
        loads('''
            namespace py foo
            namespace js bar

            include "foo.thrift"
        ''')

    assert 'thriftrw does not support including' in str(exc_info)


def test_constants(loads):
    mod = loads('''
        const i32 foo = 42;
        const string bar = "hello";
        const string baz = bar;
        const string qux = "world";

        const list<string> lst = [bar, baz, qux];
        const map<i32, string> mp = {
            1: bar,
            2: baz,
            3: qux
        };
    ''')

    assert mod.foo == 42
    assert mod.bar == 'hello'
    assert mod.baz == 'hello'
    assert mod.qux == 'world'

    assert mod.lst == ['hello', 'hello', 'world']
    assert mod.mp == {
        1: 'hello',
        2: 'hello',
        3: 'world',
    }

    # TODO forward/self referential constants


def test_undefined_constant(loads):
    with pytest.raises(ThriftCompilerError) as exc_info:
        loads('const string baz = bar')

    assert 'Unknown constant "bar"' in str(exc_info)


def test_unknown_type(loads):
    with pytest.raises(ThriftCompilerError) as exc_info:
        loads('''
            struct Foo { 1: optional Bar bar }
            struct Bar { 1: optional Baz baz }
        ''')

    assert 'Unknown type "Baz"' in str(exc_info)


def test_duplicate_constant(loads):
    with pytest.raises(ThriftCompilerError) as exc_info:
        loads('''
            const i32 foo = 42;
            const string foo = "bar"
        ''')

    assert 'Cannot define constant "foo"' in str(exc_info)
    assert 'name is already taken' in str(exc_info)


def test_duplicate_type_names(loads):
    with pytest.raises(ThriftCompilerError) as exc_info:
        loads('''
            typedef string foo

            struct foo { 1: required string bar }
        ''')

    assert 'Cannot define type "foo"' in str(exc_info)
    assert 'type with that name already exists' in str(exc_info)


def test_constant_type_conflict(loads):
    with pytest.raises(ThriftCompilerError) as exc_info:
        loads('''
            const string foo = "foo"

            struct foo { 1: required string bar }
        ''')

    assert 'Cannot define "foo"' in str(exc_info)
    assert 'name has already been used' in str(exc_info)


def test_service_type_conflict(loads):
    with pytest.raises(ThriftCompilerError) as exc_info:
        loads('''
            struct foo { 1: required string bar }
            service foo {}
        ''')

    assert 'Cannot define "foo"' in str(exc_info)
    assert 'name has already been used' in str(exc_info)
