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

from thriftrw.loader import Loader
from thriftrw.protocol import BinaryProtocol
from thriftrw.wire import mtype


service = Loader(BinaryProtocol()).loads(
    'runtime_service',
    '''
        exception GreatSadness {
            1: optional string message
        }

        service Service {
            oneway void write(1: binary data)

            i32 read()
                throws (1: GreatSadness sadness)

        }
    '''
)
Service = service.Service


@pytest.mark.parametrize('name, seqid, typ, obj, bs', [
    (b'write', 42, mtype.ONEWAY, Service.write.request(b'hello'), [
        0x00, 0x00, 0x00, 0x05,         # length:4 = 5
        0x77, 0x72, 0x69, 0x74, 0x65,   # 'write'
        0x04,                           # type:1 = ONEWAY
        0x00, 0x00, 0x00, 0x2a,         # seqid:4 = 42

        0x0B,                           # ttype:1 = BINARY
        0x00, 0x01,                     # id:2 = 1
        0x00, 0x00, 0x00, 0x05,         # length:4 = 5
        0x68, 0x65, 0x6c, 0x6c, 0x6f,   # 'hello'

        0x00,                           # STOP
    ]),
    (b'read', 127, mtype.CALL, Service.read.request(), [
        0x00, 0x00, 0x00, 0x04,         # length:4 = 5
        0x72, 0x65, 0x61, 0x64,         # 'read'
        0x01,                           # CALL
        0x00, 0x00, 0x00, 0x7f,         # seqid:4 = 127
        0x00,                           # STOP
    ]),
    (b'read', 127, mtype.REPLY, Service.read.response(success=42), [
        0x00, 0x00, 0x00, 0x04,         # length:4 = 5
        0x72, 0x65, 0x61, 0x64,         # 'read'
        0x02,                           # REPLY
        0x00, 0x00, 0x00, 0x7f,         # seqid:4 = 127

        0x08,                           # ttype:1 = i32
        0x00, 0x00,                     # id:2 = 0
        0x00, 0x00, 0x00, 0x2a,         # value = 42

        0x00,                           # STOP
    ]),
    (
        b'read',
        42,
        mtype.REPLY,
        Service.read.response(sadness=service.GreatSadness()),
        [
            0x00, 0x00, 0x00, 0x04,         # length:4 = 5
            0x72, 0x65, 0x61, 0x64,         # 'read'
            0x02,                           # REPLY
            0x00, 0x00, 0x00, 0x2a,         # seqid:4 = 42

            0x0C,                           # ttype:1 = struct
            0x00, 0x01,                     # id:2 = 1
            0x00,                           # STOP

            0x00,                           # STOP
        ],
    ),
])
def test_message_round_trips(name, seqid, typ, obj, bs):
    bs = bytes(bytearray(bs))

    assert service.dumps.message(obj, seqid) == bs

    message = service.loads.message(Service, bs)
    assert message.seqid == seqid
    assert message.message_type == typ
    assert message.name == name
    assert message.body == obj
