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
from thriftrw.errors import ThriftCompilerError


@pytest.fixture
def parse():
    return Parser().parse


@pytest.fixture
def compile(request):
    return partial(Compiler(BinaryProtocol()).compile, request.node.name)


@pytest.fixture
def loads(parse, compile):
    return (lambda s: compile(parse(s)))


def test_unknown_type(loads):
    with pytest.raises(ThriftCompilerError) as exc_info:
        loads('''
            struct Foo { 1: optional Bar bar }
            struct Bar { 1: optional Baz baz }
        ''')

    assert 'Unknown type "Baz"' in str(exc_info)


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


def test_services_and_types(loads):
    m = loads('''
        struct Foo {}
        union Bar {}

        service A {}
        service B {}

        const list<i32> z = [x, y];
        const i32 x = 42;
        const i32 y = 123;
    ''')

    assert {
        'z': [m.x, m.y],
        'x': 42,
        'y': 123,
    } == m.constants

    assert (
        m.types == (m.Foo, m.Bar) or
        m.types == (m.Bar, m.Foo)
    )

    assert (
        m.services == (m.A, m.B) or
        m.services == (m.B, m.A)
    )
