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
from thriftrw.errors import ThriftCompilerError
from thriftrw.spec.annotation import compile


@pytest.fixture
def parse():
    """Parser for group of annotations."""
    return Parser(start='annotations', silent=True).parse


@pytest.fixture
def load(parse):
    def f(s):
        return compile(parse(s))
    return f


def test_compile_none():
    assert compile(None) == {}


def test_load(load):
    assert load('(a = "b", c, d = \'e\', f)') == {
        'a': 'b', 'c': True, 'd': 'e', 'f': True
    }


def test_dupe(load):
    with pytest.raises(ThriftCompilerError) as exc_info:
        load('(a = "b", b, a = "c")')

    assert 'Annotation "a"' in str(exc_info)
    assert 'has duplicates' in str(exc_info)
