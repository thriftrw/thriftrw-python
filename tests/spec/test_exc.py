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

from thriftrw.idl import Parser
from thriftrw.spec.exc import ExceptionTypeSpec
from thriftrw.spec.field import FieldSpec
from thriftrw.spec import primitive as prim_spec


@pytest.fixture
def parse():
    return Parser(start='exception', silent=True).parse


def test_compile(parse):
    spec = ExceptionTypeSpec.compile(parse('''exception MyException {
        1: required string message
    }'''))

    assert spec.name == 'MyException'
    assert spec.fields == [
        FieldSpec(1, 'message', prim_spec.TextTypeSpec, True)
    ]


def test_load(loads):
    MyException = loads('''
        exception MyException {
            1: required string message
        }
    ''').MyException

    assert issubclass(MyException, Exception)

    with pytest.raises(MyException):
        # Must be raise-able
        raise MyException('hello world')
