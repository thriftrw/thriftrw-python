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

from thriftrw.errors import ThriftProtocolError
from thriftrw.errors import EndOfInputError
from thriftrw.protocol.binary import BinaryProtocol
from thriftrw.wire import ttype
from thriftrw.wire import value
from thriftrw.wire import Message
from thriftrw.wire.mtype import CALL, REPLY, EXCEPTION, ONEWAY

from ..util.value import (
    vbool, vbyte, vi16, vi32, vi64, vdouble, vbinary, vlist, vmap, vset,
    vstruct,
)


def reader_writer_ids(x):
    if isinstance(x, (list, value.Value)):
        return None
    return ttype.name_of(x)


@pytest.mark.parametrize('typ, bs, value', [
    # bool
    (ttype.BOOL, [0x01], vbool(True)),
    (ttype.BOOL, [0x00], vbool(False)),

    # byte
    (ttype.BYTE, [0x00], vbyte(0)),
    (ttype.BYTE, [0x01], vbyte(1)),
    (ttype.BYTE, [0xff], vbyte(-1)),
    (ttype.BYTE, [0x7f], vbyte(127)),
    (ttype.BYTE, [0x80], vbyte(-128)),

    # i16
    (ttype.I16, [0x00, 0x01], vi16(1)),
    (ttype.I16, [0x00, 0xff], vi16(255)),
    (ttype.I16, [0x01, 0x00], vi16(256)),
    (ttype.I16, [0x01, 0x01], vi16(257)),
    (ttype.I16, [0x7f, 0xff], vi16(32767)),
    (ttype.I16, [0xff, 0xff], vi16(-1)),
    (ttype.I16, [0xff, 0xfe], vi16(-2)),
    (ttype.I16, [0xff, 0x00], vi16(-256)),
    (ttype.I16, [0xff, 0x01], vi16(-255)),
    (ttype.I16, [0x80, 0x00], vi16(-32768)),

    # i32
    (ttype.I32, [0x00, 0x00, 0x00, 0x01], vi32(1)),
    (ttype.I32, [0x00, 0x00, 0x00, 0xff], vi32(255)),
    (ttype.I32, [0x00, 0x00, 0xff, 0xff], vi32(65535)),
    (ttype.I32, [0x00, 0xff, 0xff, 0xff], vi32(16777215)),
    (ttype.I32, [0x7f, 0xff, 0xff, 0xff], vi32(2147483647)),
    (ttype.I32, [0xff, 0xff, 0xff, 0xff], vi32(-1)),
    (ttype.I32, [0xff, 0xff, 0xff, 0x00], vi32(-256)),
    (ttype.I32, [0xff, 0xff, 0x00, 0x00], vi32(-65536)),
    (ttype.I32, [0xff, 0x00, 0x00, 0x00], vi32(-16777216)),
    (ttype.I32, [0x80, 0x00, 0x00, 0x00], vi32(-2147483648)),

    # i64
    (ttype.I64,
     [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01],
     vi64(1)),
    (ttype.I64,
     [0x00, 0x00, 0x00, 0x00, 0xff, 0xff, 0xff, 0xff],
     vi64(4294967295)),
    (ttype.I64,
     [0x00, 0x00, 0x00, 0xff, 0xff, 0xff, 0xff, 0xff],
     vi64(1099511627775)),
    (ttype.I64,
     [0x00, 0x00, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff],
     vi64(281474976710655)),
    (ttype.I64,
     [0x00, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff],
     vi64(72057594037927935)),
    (ttype.I64,
     [0x7f, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff],
     vi64(9223372036854775807)),
    (ttype.I64,
     [0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff],
     vi64(-1)),
    (ttype.I64,
     [0xff, 0xff, 0xff, 0xff, 0x00, 0x00, 0x00, 0x00],
     vi64(-4294967296)),
    (ttype.I64,
     [0xff, 0xff, 0xff, 0x00, 0x00, 0x00, 0x00, 0x00],
     vi64(-1099511627776)),
    (ttype.I64,
     [0xff, 0xff, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
     vi64(-281474976710656)),
    (ttype.I64,
     [0xff, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
     vi64(-72057594037927936)),
    (ttype.I64,
     [0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
     vi64(-9223372036854775808)),

    # double
    (ttype.DOUBLE,
     [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
     vdouble(0.0)),
    (ttype.DOUBLE,
     [0x3f, 0xf0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
     vdouble(1.0)),
    (ttype.DOUBLE,
     [0x3f, 0xf0, 0x0, 0x0, 0x0, 0x6, 0xdf, 0x38],
     vdouble(1.0000000001)),
    (ttype.DOUBLE,
     [0x3f, 0xf1, 0x99, 0x99, 0x99, 0x99, 0x99, 0x9a],
     vdouble(1.1)),
    (ttype.DOUBLE,
     [0xbf, 0xf1, 0x99, 0x99, 0x99, 0x99, 0x99, 0x9a],
     vdouble(-1.1)),
    (ttype.DOUBLE,
     [0x40, 0x9, 0x21, 0xfb, 0x54, 0x44, 0x2d, 0x18],
     vdouble(3.141592653589793)),
    (ttype.DOUBLE,
     [0xbf, 0xf0, 0x0, 0x0, 0x0, 0x6, 0xdf, 0x38],
     vdouble(-1.0000000001)),

    # binary = len:4 (.){len}
    (ttype.BINARY, [0x00, 0x00, 0x00, 0x00], vbinary(b'')),
    (ttype.BINARY, [
        0x00, 0x00, 0x00, 0x05,         # len:4 = 5
        0x68, 0x65, 0x6c, 0x6c, 0x6f,   # 'h', 'e', 'l', 'l', 'o'
    ], vbinary(b'hello')),

    # struct = (type:1 id:2 value)* stop
    # stop = 0
    (ttype.STRUCT, [0x00], vstruct()),
    (ttype.STRUCT, [
        0x02,        # type:1 = bool
        0x00, 0x01,  # id:2 = 1
        0x01,        # value = true
        0x00,        # stop
    ], vstruct((1, ttype.BOOL, vbool(True)))),
    (ttype.STRUCT, [
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
        (1, ttype.I16, vi16(42)),
        (2, ttype.LIST, vlist(
            ttype.BINARY, vbinary(b'foo'), vbinary(b'bar'))),
    )),

    # map = ktype:1 vtype:1 count:4 (key value){count}
    (ttype.MAP, [0x0A, 0X0B, 0x00, 0x00, 0x00, 0x00],
     vmap(ttype.I64, ttype.BINARY)),
    (ttype.MAP, [
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
        ttype.BINARY, ttype.LIST,
        (vbinary(b'a'), vlist(ttype.BYTE, vbyte(1))),
        (vbinary(b'b'), vlist(ttype.I16, vi16(2), vi16(3))),
    )),

    # set = vtype:1 count:4 (value){count)
    (ttype.SET, [0x02, 0x00, 0x00, 0x00, 0x00], vset(ttype.BOOL)),
    (ttype.SET, [
        0x02, 0x00, 0x00, 0x00, 0x03, 0x01, 0x00, 0x01
    ], vset(ttype.BOOL, vbool(True), vbool(False), vbool(True))),

    # list = vtype:1 count:4 (value){count}
    (ttype.LIST, [0x0C, 0x00, 0x00, 0x00, 0x00], vlist(ttype.STRUCT)),
    (ttype.LIST, [
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
        ttype.STRUCT,
        vstruct((1, ttype.I16, vi16(1)), (2, ttype.I32, vi32(2))),
        vstruct((1, ttype.I16, vi16(3)), (2, ttype.I32, vi32(4))),
    )),
], ids=reader_writer_ids)
def test_reader_and_writer(typ, bs, value):
    """Test serialization and deserialization of all samples."""
    bs = bytes(bytearray(bs))

    protocol = BinaryProtocol()

    result = protocol.deserialize_value(typ, bs)
    assert value == result

    result = protocol.serialize_value(value)
    assert bs == result


@pytest.mark.parametrize('typ, bs', [
    (ttype.BOOL, []),
    (ttype.BYTE, []),
    (ttype.DOUBLE, [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07]),
    (ttype.I16, [0x01]),
    (ttype.I32, [0x01, 0x02, 0x03]),
    (ttype.I64, [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07]),

    (ttype.BINARY, []),
    (ttype.BINARY, [0x00, 0x00, 0x00, 0x01]),
    (ttype.BINARY, [0x00, 0x00, 0x00, 0x05, 0x68, 0x65, 0x6c, 0x6c]),

    (ttype.STRUCT, []),
    (ttype.STRUCT, [0x02, 0x01]),
    (ttype.STRUCT, [0x06, 0x00, 0x01, 0x00, 0x01]),

    (ttype.MAP, []),
    (ttype.MAP, [0x02, 0x03]),
    (ttype.MAP, [0x02, 0x03, 0x00, 0x00, 0x00, 0x01]),
    (ttype.MAP, [
        0x02, 0x03,                 # ktype vtype
        0x00, 0x00, 0x00, 0x02,     # len = 2
        0x00, 0x01,                 # (False, 1)
        0x01                        # (True, ?)
    ]),

    (ttype.SET, []),
    (ttype.SET, [0x02]),
    (ttype.SET, [0x02, 0x00, 0x00, 0x00]),
    (ttype.SET, [0x02, 0x00, 0x00, 0x00, 0x01]),
    (ttype.SET, [
        0x02,                    # typ
        0x00, 0x00, 0x00, 0x02,  # len = 2
        0x01,                    # True
    ]),

    (ttype.LIST, []),
    (ttype.LIST, [0x02]),
    (ttype.LIST, [0x02, 0x00, 0x00, 0x00]),
    (ttype.LIST, [0x02, 0x00, 0x00, 0x00, 0x01]),
    (ttype.LIST, [
        0x02,                    # typ
        0x00, 0x00, 0x00, 0x02,  # len = 2
        0x01,                    # True
    ]),
], ids=reader_writer_ids)
def test_input_too_short(typ, bs):
    """Test that EndOfInputError is raised when not enough bytes are
    available."""

    protocol = BinaryProtocol()

    with pytest.raises(EndOfInputError) as exc_info:
        protocol.deserialize_value(typ, bytes(bytearray(bs)))

    assert 'bytes but got' in str(exc_info)


@pytest.mark.parametrize('typ, bs', [
    (0x00, []),
    (ttype.STRUCT, [
        0x01,
        0x00, 0x01,
    ]),
    (ttype.MAP, [
        0x05, 0x07,
        0x00, 0x00, 0x00, 0x00,
    ]),
    (ttype.SET, [
        0x09,
        0x00, 0x00, 0x00, 0x00,
    ]),
    (ttype.LIST, [
        0x16,
        0x00, 0x00, 0x00, 0x00,
    ]),
], ids=reader_writer_ids)
def test_unknown_type_id(typ, bs):
    protocol = BinaryProtocol()

    with pytest.raises(ThriftProtocolError) as exc_info:
        protocol.deserialize_value(typ, bytes(bytearray(bs)))

    assert 'Unknown TType' in str(exc_info)


@pytest.mark.parametrize('bs, message', [
    ([
        0x00, 0x00, 0x00, 0x06,                 # length = 6
        0x67, 0x65, 0x74, 0x46, 0x6f, 0x6f,     # 'getFoo'

        0x01,                       # type = CALL
        0x00, 0x00, 0x00, 0x2a,     # seqId = 42

        0x00,
    ], Message(
        name='getFoo',
        seqid=42,
        message_type=CALL,
        body=vstruct()
    )),
    ([
        0x00, 0x00, 0x00, 0x06,                 # length = 6
        0x73, 0x65, 0x74, 0x42, 0x61, 0x72,     # 'setBar'

        0x02,                       # type = REPLY
        0x00, 0x00, 0x00, 0x01,     # seqId = 1

        0x02, 0x00, 0x01, 0x01,     # {1: True}
        0x00,
    ], Message(
        name='setBar',
        seqid=1,
        message_type=REPLY,
        body=vstruct((1, ttype.BOOL, vbool(True))),
    )),
])
def test_message_round_trip(bs, message):
    bs = bytes(bytearray(bs))
    protocol = BinaryProtocol()

    result = protocol.deserialize_message(bs)
    assert message == result

    result = protocol.serialize_message(message)
    assert bs == result


@pytest.mark.parametrize('bs, message', [
    ([
        0x80, 0x01,  # version = 1
        0x00, 0x03,  # type = EXCEPTION

        0x00, 0x00, 0x00, 0x06,                 # length = 6
        0x67, 0x65, 0x74, 0x46, 0x6f, 0x6f,     # 'getFoo'

        0x00, 0x00, 0x00, 0x2a,     # seqId = 42

        0x02, 0x00, 0x08, 0x00,     # {8: False}
        0x00,
    ], Message(
        name='getFoo',
        seqid=42,
        message_type=EXCEPTION,
        body=vstruct((8, ttype.BOOL, vbool(False))),
    )),
    ([
        0x80, 0x01,  # version = 1
        0x00, 0x04,  # type = ONEWAY

        0x00, 0x00, 0x00, 0x06,                 # length = 6
        0x73, 0x65, 0x74, 0x42, 0x61, 0x72,     # 'setBar'

        0x00, 0x00, 0x00, 0x01,     # seqId = 1

        0x00,
    ], Message(
        name='setBar',
        seqid=1,
        message_type=ONEWAY,
        body=vstruct(),
    )),
])
def test_message_parse_strict(bs, message):
    bs = bytes(bytearray(bs))
    protocol = BinaryProtocol()

    result = protocol.deserialize_message(bs)
    assert message == result


@pytest.mark.parametrize('bs', [
    [
        0x80, 0x2a,  # version = 42
        0x00, 0x01,  # type = CALL
        0x00, 0x00, 0x00, 0x06,                 # length = 6
        0x67, 0x65, 0x74, 0x46, 0x6f, 0x6f,     # 'getFoo'
        0x00, 0x00, 0x00, 0x01,     # seqId = 1
        0x00,   # STOP
    ]
])
def test_message_invalid_version(bs):
    bs = bytes(bytearray(bs))

    with pytest.raises(ThriftProtocolError) as exc_info:
        BinaryProtocol().deserialize_message(bs)

    assert 'Unsupported version "42"' in str(exc_info)
