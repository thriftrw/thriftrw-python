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
from six import BytesIO

from thriftrw.protocol.exceptions import ThriftProtocolError
from thriftrw.protocol.exceptions import EndOfInputError
from thriftrw.protocol.binary import BinaryProtocolReader
from thriftrw.protocol.binary import BinaryProtocolWriter
from thriftrw.protocol.binary import BinaryProtocol
from thriftrw.wire import TType
from thriftrw.wire import value

from ..util.value import *  # noqa


def reader_writer_ids(x):
    if isinstance(x, list) or isinstance(x, value.Value) or x not in TType:
        return None
    return {
        TType.BOOL: 'bool',
        TType.BYTE: 'byte',
        TType.DOUBLE: 'double',
        TType.I16: 'i16',
        TType.I32: 'i32',
        TType.I64: 'i64',
        TType.BINARY: 'binary',
        TType.STRUCT: 'struct',
        TType.MAP: 'map',
        TType.SET: 'set',
        TType.LIST: 'list',
    }[x]


@pytest.mark.parametrize('typ, bytes, value', [
    # bool
    (TType.BOOL, [0x01], vbool(True)),
    (TType.BOOL, [0x00], vbool(False)),

    # byte
    (TType.BYTE, [0x00], vbyte(0)),
    (TType.BYTE, [0x01], vbyte(1)),
    (TType.BYTE, [0xff], vbyte(-1)),
    (TType.BYTE, [0x7f], vbyte(127)),
    (TType.BYTE, [0x80], vbyte(-128)),

    # i16
    (TType.I16, [0x00, 0x01], vi16(1)),
    (TType.I16, [0x00, 0xff], vi16(255)),
    (TType.I16, [0x01, 0x00], vi16(256)),
    (TType.I16, [0x01, 0x01], vi16(257)),
    (TType.I16, [0x7f, 0xff], vi16(32767)),
    (TType.I16, [0xff, 0xff], vi16(-1)),
    (TType.I16, [0xff, 0xfe], vi16(-2)),
    (TType.I16, [0xff, 0x00], vi16(-256)),
    (TType.I16, [0xff, 0x01], vi16(-255)),
    (TType.I16, [0x80, 0x00], vi16(-32768)),

    # i32
    (TType.I32, [0x00, 0x00, 0x00, 0x01], vi32(1)),
    (TType.I32, [0x00, 0x00, 0x00, 0xff], vi32(255)),
    (TType.I32, [0x00, 0x00, 0xff, 0xff], vi32(65535)),
    (TType.I32, [0x00, 0xff, 0xff, 0xff], vi32(16777215)),
    (TType.I32, [0x7f, 0xff, 0xff, 0xff], vi32(2147483647)),
    (TType.I32, [0xff, 0xff, 0xff, 0xff], vi32(-1)),
    (TType.I32, [0xff, 0xff, 0xff, 0x00], vi32(-256)),
    (TType.I32, [0xff, 0xff, 0x00, 0x00], vi32(-65536)),
    (TType.I32, [0xff, 0x00, 0x00, 0x00], vi32(-16777216)),
    (TType.I32, [0x80, 0x00, 0x00, 0x00], vi32(-2147483648)),

    # i64
    (TType.I64,
     [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01],
     vi64(1)),
    (TType.I64,
     [0x00, 0x00, 0x00, 0x00, 0xff, 0xff, 0xff, 0xff],
     vi64(4294967295)),
    (TType.I64,
     [0x00, 0x00, 0x00, 0xff, 0xff, 0xff, 0xff, 0xff],
     vi64(1099511627775)),
    (TType.I64,
     [0x00, 0x00, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff],
     vi64(281474976710655)),
    (TType.I64,
     [0x00, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff],
     vi64(72057594037927935)),
    (TType.I64,
     [0x7f, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff],
     vi64(9223372036854775807)),
    (TType.I64,
     [0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff],
     vi64(-1)),
    (TType.I64,
     [0xff, 0xff, 0xff, 0xff, 0x00, 0x00, 0x00, 0x00],
     vi64(-4294967296)),
    (TType.I64,
     [0xff, 0xff, 0xff, 0x00, 0x00, 0x00, 0x00, 0x00],
     vi64(-1099511627776)),
    (TType.I64,
     [0xff, 0xff, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
     vi64(-281474976710656)),
    (TType.I64,
     [0xff, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
     vi64(-72057594037927936)),
    (TType.I64,
     [0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
     vi64(-9223372036854775808)),

    # double
    (TType.DOUBLE,
     [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
     vdouble(0.0)),
    (TType.DOUBLE,
     [0x3f, 0xf0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
     vdouble(1.0)),
    (TType.DOUBLE,
     [0x3f, 0xf0, 0x0, 0x0, 0x0, 0x6, 0xdf, 0x38],
     vdouble(1.0000000001)),
    (TType.DOUBLE,
     [0x3f, 0xf1, 0x99, 0x99, 0x99, 0x99, 0x99, 0x9a],
     vdouble(1.1)),
    (TType.DOUBLE,
     [0xbf, 0xf1, 0x99, 0x99, 0x99, 0x99, 0x99, 0x9a],
     vdouble(-1.1)),
    (TType.DOUBLE,
     [0x40, 0x9, 0x21, 0xfb, 0x54, 0x44, 0x2d, 0x18],
     vdouble(3.141592653589793)),
    (TType.DOUBLE,
     [0xbf, 0xf0, 0x0, 0x0, 0x0, 0x6, 0xdf, 0x38],
     vdouble(-1.0000000001)),

    # binary = len:4 (.){len}
    (TType.BINARY, [0x00, 0x00, 0x00, 0x00], vbinary(b'')),
    (TType.BINARY, [
        0x00, 0x00, 0x00, 0x05,         # len:4 = 5
        0x68, 0x65, 0x6c, 0x6c, 0x6f,   # 'h', 'e', 'l', 'l', 'o'
    ], vbinary(b'hello')),

    # struct = (type:1 id:2 value)* stop
    # stop = 0
    (TType.STRUCT, [0x00], vstruct()),
    (TType.STRUCT, [
        0x02,        # type:1 = bool
        0x00, 0x01,  # id:2 = 1
        0x01,        # value = true
        0x00,        # stop
    ], vstruct((1, TType.BOOL, vbool(True)))),
    (TType.STRUCT, [
        0x06,           # type:1 = i16
        0x00, 0x01,     # id:2 = 1
        0x00, 0x2a,     # value = 42

        0x0F,           # type:1 = list
        0x00, 0x02,     # id:2 = 2

        # <list>
        0x0B,                       # type:1 = binary
        0x00, 0x00, 0x00, 0x02,     # size:4 = 2
        # <binary>
        0x00, 0x00, 0x00, 0x03,     # len:4 = 3
        0x66, 0x6f, 0x6f,           # 'f', 'o', 'o'
        # </binary>
        # <binary>
        0x00, 0x00, 0x00, 0x03,     # len:4 = 3
        0x62, 0x61, 0x72,           # 'b', 'a', 'r'
        # </binary>
        # </list>

        0x00,           # stop
    ], vstruct(
        (1, TType.I16, vi16(42)),
        (2, TType.LIST, vlist(
            TType.BINARY, vbinary(b'foo'), vbinary(b'bar'))),
    )),

    # map = ktype:1 vtype:1 count:4 (key value){count}
    (TType.MAP, [0x0A, 0X0B, 0x00, 0x00, 0x00, 0x00],
     vmap(TType.I64, TType.BINARY)),
    (TType.MAP, [
        0x0B,   # ktype = binary
        0x0F,   # vtype = list
        0x00, 0x00, 0x00, 0x02,   # count:4 = 2

        # <item>
        # <key>
        0x00, 0x00, 0x00, 0x01,  # len:4 = 1
        0x61,                    # 'a'
        # </key>
        # <value>
        0x03,                    # type:1 = byte
        0x00, 0x00, 0x00, 0x01,  # count:4 = 1
        0x01,                    # 1
        # </value>
        # </item>

        # <item>
        # <key>
        0x00, 0x00, 0x00, 0x01,  # len:4 = 1
        0x62,                    # 'b'
        # </key>
        # <value>
        0x06,                    # type:1 = 6
        0x00, 0x00, 0x00, 0x02,  # count:4 = 2
        0x00, 0x02,              # 2
        0x00, 0x03,              # 3
        # </value>
        # </item>
    ], vmap(
        TType.BINARY, TType.LIST,
        (vbinary(b'a'), vlist(TType.BYTE, vbyte(1))),
        (vbinary(b'b'), vlist(TType.I16, vi16(2), vi16(3))),
    )),

    # set = vtype:1 count:4 (value){count)
    (TType.SET, [0x02, 0x00, 0x00, 0x00, 0x00], vset(TType.BOOL)),
    (TType.SET, [
        0x02, 0x00, 0x00, 0x00, 0x03, 0x01, 0x00, 0x01
    ], vset(TType.BOOL, vbool(True), vbool(False), vbool(True))),

    # list = vtype:1 count:4 (value){count}
    (TType.LIST, [0x0C, 0x00, 0x00, 0x00, 0x00], vset(TType.STRUCT)),
    (TType.LIST, [
        0x0C,                       # vtype:1 = struct
        0x00, 0x00, 0x00, 0x02,     # count:4 = 2

        # <struct>
        0x06,        # type:1 = i16
        0x00, 0x01,  # id:2 = 1
        0x00, 0x01,  # value = 1

        0x08,                    # type:1 = i32
        0x00, 0x02,              # id:2 = 2
        0x00, 0x00, 0x00, 0x02,  # value = 2

        0x00,        # stop
        # </struct>

        # <struct>
        0x06,        # type:1 = i16
        0x00, 0x01,  # id:2 = 1
        0x00, 0x03,  # value = 3

        0x08,                    # type:1 = i32
        0x00, 0x02,              # id:2 = 2
        0x00, 0x00, 0x00, 0x04,  # value = 4

        0x00,        # stop
        # </struct>
    ], vlist(
        TType.STRUCT,
        vstruct((1, TType.I16, vi16(1)), (2, TType.I32, vi32(2))),
        vstruct((1, TType.I16, vi16(3)), (2, TType.I32, vi32(4))),
    )),
], ids=reader_writer_ids)
def test_reader_and_writer(typ, bytes, value):
    """Test serialization and deserialization of all samples."""
    bytes = bytearray(bytes)

    protocol = BinaryProtocol()

    result = protocol.deserialize_value(typ, bytes)
    assert value == result

    result = protocol.serialize_value(value)
    assert bytes == result


@pytest.mark.parametrize('typ, bytes', [
    (TType.BOOL, []),
    (TType.BYTE, []),
    (TType.DOUBLE, [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07]),
    (TType.I16, [0x01]),
    (TType.I32, [0x01, 0x02, 0x03]),
    (TType.I64, [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07]),

    (TType.BINARY, []),
    (TType.BINARY, [0x00, 0x00, 0x00, 0x01]),
    (TType.BINARY, [0x00, 0x00, 0x00, 0x05, 0x68, 0x65, 0x6c, 0x6c]),

    (TType.STRUCT, []),
    (TType.STRUCT, [0x02, 0x01]),
    (TType.STRUCT, [0x06, 0x00, 0x01, 0x00, 0x01]),

    (TType.MAP, []),
    (TType.MAP, [0x02, 0x03]),
    (TType.MAP, [0x02, 0x03, 0x00, 0x00, 0x00, 0x01]),
    (TType.MAP, [
        0x02, 0x03,                 # ktype vtype
        0x00, 0x00, 0x00, 0x02,     # len = 2
        0x00, 0x01,                 # (False, 1)
        0x01                        # (True, ?)
    ]),

    (TType.SET, []),
    (TType.SET, [0x02]),
    (TType.SET, [0x02, 0x00, 0x00, 0x00]),
    (TType.SET, [0x02, 0x00, 0x00, 0x00, 0x01]),
    (TType.SET, [
        0x02,                    # typ
        0x00, 0x00, 0x00, 0x02,  # len = 2
        0x01,                    # True
    ]),

    (TType.LIST, []),
    (TType.LIST, [0x02]),
    (TType.LIST, [0x02, 0x00, 0x00, 0x00]),
    (TType.LIST, [0x02, 0x00, 0x00, 0x00, 0x01]),
    (TType.LIST, [
        0x02,                    # typ
        0x00, 0x00, 0x00, 0x02,  # len = 2
        0x01,                    # True
    ]),
], ids=reader_writer_ids)
def test_input_too_short(typ, bytes):
    """Test that EndOfInputError is raised when not enough bytes are
    available."""

    reader = BinaryProtocolReader(BytesIO(bytearray(bytes)))
    with pytest.raises(EndOfInputError) as exc_info:
        reader.read(typ)
    assert 'bytes but got' in str(exc_info)


@pytest.mark.parametrize('typ, bytes', [
    (0x00, []),
    (TType.STRUCT, [
        0x01,
        0x00, 0x01,
    ]),
    (TType.MAP, [
        0x05, 0x07,
        0x00, 0x00, 0x00, 0x00,
    ]),
    (TType.SET, [
        0x09,
        0x00, 0x00, 0x00, 0x00,
    ]),
    (TType.LIST, [
        0x16,
        0x00, 0x00, 0x00, 0x00,
    ]),
], ids=reader_writer_ids)
def test_unknown_type_id(typ, bytes):
    reader = BinaryProtocolReader(BytesIO(bytearray(bytes)))
    with pytest.raises(ThriftProtocolError) as exc_info:
        reader.read(typ)
    assert 'Unknown TType' in str(exc_info)

@pytest.mark.parametrize('typ, bytes, value', [
    (typ, 0x00, vi16(0)) for typ in TType
], ids=reader_writer_ids)
def test_backwards_compatibility_with_python_266(typ, bytes, value):

    class SawExpectedType(Exception):
        pass

    class TestProtocolReader(BinaryProtocolReader):
        def _unpack(self, num_bytes, spec):
            assert type(spec) is type(b'')
            raise SawExpectedType()

    class TestProtocolWriter(BinaryProtocolWriter):
        def _pack(self, spec, value):
            assert type(spec) is type(b'')
            raise SawExpectedType()

    class TestProtocol(BinaryProtocol):
        reader_class = TestProtocolReader
        writer_class = TestProtocolWriter

    with pytest.raises(SawExpectedType):
        protocol = TestProtocol()
        protocol.deserialize_value(typ, bytes)

    with pytest.raises(SawExpectedType):
        protocol = TestProtocol()
        protocol.serialize_value(value)
