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
import doubles
from doubles import expect

from thriftrw.wire import value
from thriftrw.wire import TType


@pytest.mark.parametrize('value, visit_name, visit_args', [
    # Primitives
    (value.BoolValue(True), 'visit_bool', [True]),
    (value.ByteValue(42), 'visit_byte', [42]),
    (value.DoubleValue(12.34), 'visit_double', [12.34]),
    (value.I16Value(1234), 'visit_i16', [1234]),
    (value.I32Value(39813), 'visit_i32', [39813]),
    (value.I64Value(198735315), 'visit_i64', [198735315]),
    (value.BinaryValue(b'hello world'), 'visit_binary', [b'hello world']),

    # Struct
    (value.StructValue([
        value.FieldValue(1, TType.BOOL, value.BoolValue(True)),
        value.FieldValue(2, TType.BYTE, value.ByteValue(42)),
    ]), 'visit_struct', [[
        value.FieldValue(1, TType.BOOL, value.BoolValue(True)),
        value.FieldValue(2, TType.BYTE, value.ByteValue(42)),
    ]]),

    # Map
    (value.MapValue(TType.BINARY, TType.I16, [
        (value.BinaryValue('Hello'), value.I16Value(1)),
        (value.BinaryValue('World'), value.I16Value(2)),
    ]), 'visit_map', [TType.BINARY, TType.I16, [
        (value.BinaryValue('Hello'), value.I16Value(1)),
        (value.BinaryValue('World'), value.I16Value(2)),
    ]]),

    # Set
    (value.SetValue(TType.I32, [
        value.I32Value(1234),
        value.I32Value(4567),
    ]), 'visit_set', [TType.I32, [
        value.I32Value(1234),
        value.I32Value(4567),
    ]]),

    # List
    (value.ListValue(TType.I64, [
        value.I64Value(1380),
        value.I64Value(1479),
    ]), 'visit_list', [TType.I64, [
        value.I64Value(1380),
        value.I64Value(1479),
    ]]),
])
def test_visitors(value, visit_name, visit_args):
    """Checks that for each value type, the correct visitor is called."""

    visitor = doubles.InstanceDouble('thriftrw.wire.ValueVisitor')
    getattr(
        expect(visitor), visit_name
    ).with_args(*visit_args).and_return('hello').once()
    assert 'hello' == value.apply(visitor)


def test_struct_get():
    struct = value.StructValue([
        value.FieldValue(1, TType.BOOL, value.BoolValue(True)),
        value.FieldValue(2, TType.BYTE, value.ByteValue(42)),
        value.FieldValue(3, TType.LIST, value.ListValue(
            TType.BINARY,
            [
                value.BinaryValue('Hello'),
                value.BinaryValue('World'),
            ]
        )),
    ])

    assert struct.get(1, TType.BOOL).value
    assert value.ByteValue(42) == struct.get(2, TType.BYTE).value
    assert value.ListValue(TType.BINARY, [
        value.BinaryValue('Hello'),
        value.BinaryValue('World'),
    ]) == struct.get(3, TType.LIST).value

    assert not struct.get(1, TType.BINARY)
