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

import pytest

import thriftrw.protocol


@pytest.fixture
def struct(loads):
    Struct = loads('''struct Struct {
        1: required list<string> strings;
        2: required set<i32> ints;
        3: required map<i32, string> mapped;
    }''').Struct

    return Struct(
        strings=['foo'] * 100,
        ints=set([256] * 100),
        mapped={n: 'bar' for n in range(100)},
    )


def test_binary_dumps(benchmark, struct):
    protocol = thriftrw.protocol.BinaryProtocol()

    benchmark(lambda: protocol.dumps(struct))


def test_binary_loads(benchmark, struct):
    protocol = thriftrw.protocol.BinaryProtocol()
    serialized = protocol.dumps(struct)

    benchmark(lambda: protocol.loads(struct.__class__, serialized))


def test_to_primitive(benchmark, struct):
    benchmark(struct.to_primitive)


def test_from_primitive(benchmark, struct):
    primitive = struct.to_primitive()

    benchmark(lambda: struct.type_spec.from_primitive(primitive))
