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

from thriftrw.idl import ast
from thriftrw.idl.parser import Parser
from thriftrw.errors import ThriftParserError


@pytest.mark.parametrize('s', [
    # we disallow 0 as a field ID at the parser level
    'struct Foo { 0: string foo }',
    'service Bar {',
    'service { }',
    'typedef i64 foo (bar = )',
])
def test_parse_errors(s):
    with pytest.raises(ThriftParserError):
        Parser().parse(s)


@pytest.mark.parametrize('start, expected, s', [
    # type annotations
    ('annotations', [], ''),
    ('annotations', [], '()'),
    ('annotations', [
        ast.Annotation('foo', True, 1),
        ast.Annotation('bar', 'baz', 1),
        ast.Annotation('qux', True, 1),
    ], "(foo, bar = 'baz', qux)"),

    # constants
    (
        'const_value',
        ast.ConstReference('SomeEnum.someItem', 1),
        'SomeEnum.someItem',
    ),
    (
        'const_value',
        ast.ConstList(
            values=[
                ast.ConstPrimitiveValue(1, 1),
                ast.ConstPrimitiveValue(2, 1),
                ast.ConstPrimitiveValue(3, 1),
            ],
            lineno=1,
        ),
        '[1, 2, 3]',
    ),
    (
        'const_value',
        ast.ConstMap(
            pairs={
                ast.ConstPrimitiveValue('x', 1): ast.ConstReference('y', 1),
                ast.ConstPrimitiveValue('baz', 1): ast.ConstReference(42, 1),
            },
            lineno=1,
        ),
        '{"x": y, "baz": 42}',
    ),

    # field types
    ('field_type', ast.PrimitiveType('byte', []), 'byte'),
    ('field_type', ast.PrimitiveType('byte', []), 'i8'),  # i8 == byte
    ('field_type', ast.PrimitiveType('i16', []), 'i16'),
    (
        'field_type',
        ast.PrimitiveType('i32', [
            ast.Annotation('foo', 'bar', 1),
            ast.Annotation('baz', 'qux', 1),
        ]),
        'i32 (foo = "bar", baz = "qux")',
    ),

    (
        # typedef with annotations on both, the typedef and the arguments.
        'typedef',
        ast.Typedef(
            name='Integer',
            target_type=ast.PrimitiveType('i32', [
                ast.Annotation('foo', 'bar', 3),
                ast.Annotation('baz', 'qux', 4),
            ]),
            annotations=[
                ast.Annotation('boxed', 'true', 5),
                ast.Annotation('bounded', True, 5),
            ],
            lineno=5,
        ),
        """
        typedef i32 (
            foo = "bar";
            baz = "qux";
        ) Integer (boxed = "true", bounded)
        """,
    ),
])
def test_parse_ast(start, expected, s):
    assert expected == Parser(start=start, silent=True).parse(s)
