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
        mapped={n: 'bar' for n in xrange(100)},
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
