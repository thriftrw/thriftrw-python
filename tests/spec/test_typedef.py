# Copyright (c) 2016 Uber Technologies, Inc.
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

from thriftrw.spec.reference import TypeReference
from thriftrw.spec.typedef import TypedefTypeSpec
from thriftrw.spec import primitive as prim_spec
from thriftrw.idl import Parser


@pytest.fixture
def parse():
    """Parser for enum definitions."""
    return Parser(start='typedef', silent=True).parse


def test_compile(parse):
    assert TypedefTypeSpec.compile(parse('typedef i32 ID')) == (
        TypedefTypeSpec('ID', prim_spec.I32TypeSpec)
    )

    assert TypedefTypeSpec.compile(parse('typedef Custom Foo')) == (
        TypedefTypeSpec('Foo', TypeReference('Custom', 1))
    )


def test_link(loads):
    mod = loads('''
        typedef Bar Foo
        typedef Baz Bar
        typedef Qux Baz

        struct Qux {
            1: required i32 x
        }
    ''')

    assert mod.Foo is mod.Bar
    assert mod.Bar is mod.Baz
    assert mod.Baz is mod.Qux
