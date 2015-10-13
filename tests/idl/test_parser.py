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

from thriftrw.idl import ast
from thriftrw.idl.parser import Parser
from thriftrw.errors import ThriftParserError


@pytest.mark.parametrize('s', [
    # we disallow 0 as a field ID at the parser level
    'struct Foo { 0: string foo }',
    'service Bar {',
    'service { }',
])
def test_parse_errors(s):
    with pytest.raises(ThriftParserError):
        Parser().parse(s)


def test_parse_annotations():
    assert ast.Typedef(
        name='Integer',
        target_type=ast.PrimitiveType(
            name='i32',
            annotations=[
                ast.Annotation('foo', 'bar', lineno=2),
                ast.Annotation('baz', 'qux', lineno=3),
            ]
        ),
        annotations=[ast.Annotation('boxed', 'true', lineno=4)],
        lineno=4,
    ) == Parser(start='typedef', silent=True).parse(
        '''typedef i32 (
            foo = "bar";
            baz = "qux";
        ) Integer (boxed = "true")'''
    )
