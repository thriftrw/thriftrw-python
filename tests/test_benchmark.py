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

import thriftrw


@pytest.fixture(scope='session')
def module(request):
    return thriftrw.loader.Loader().loads('benchmark', '''
        struct PrimitiveContainers {
            1: required list<string> strings;
            2: required set<i32> ints;
            3: required map<i32, string> mapped;
        }

        struct Point {
            1: required double x;
            2: required double y;
        }

        struct Edge {
            1: required Point start;
            2: required Point end;
        }

        struct Graph { 1: required list<Edge> edges }
    ''')


@pytest.fixture(params=[
    'primitive_containers',
    'nested_structs',
])
def value(module, request):
    if request.param == 'primitive_containers':
        return module.PrimitiveContainers(
            strings=['foo'] * 100000,
            ints=set(range(100000)),
            mapped={n: 'bar' for n in range(100000)},
        )
    elif request.param == 'nested_structs':
        return module.Graph(edges=[
            module.Edge(
                start=module.Point(1.23, 4.56),
                end=module.Point(1.23, 4.56),
            ) for i in range(1000)
        ])
    else:
        raise NotImplementedError


def test_binary_dumps(benchmark, module, value):
    benchmark(module.dumps, value)


def test_binary_loads(benchmark, module, value):
    serialized = module.dumps(value)
    benchmark(module.loads, value.__class__, serialized)


def test_to_primitive(benchmark, value):
    benchmark(value.to_primitive)


def test_from_primitive(benchmark, value):
    primitive = value.to_primitive()
    benchmark(value.type_spec.from_primitive, primitive)
