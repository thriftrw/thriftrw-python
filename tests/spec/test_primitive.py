# encoding=utf8
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

from thriftrw.spec.primitive import TextTypeSpec
from thriftrw.wire.value import BinaryValue


@pytest.mark.parametrize('args', [
    (u'☃', b'\xe2\x98\x83', None),
    (b'\xe2\x98\x83', b'\xe2\x98\x83', u'☃'),
    (b'foo', b'foo', u'foo'),
])
def test_text_round_trip(args):
    # workaround for pytest-dev/pytest#1086 until pytest 2.8.2 is released.
    s, val, out = args
    if out is None:
        out = s

    wire_val = TextTypeSpec.to_wire(s)
    assert wire_val == BinaryValue(val)
    assert TextTypeSpec.from_wire(wire_val) == out


@pytest.mark.parametrize('args', [
    (u'☃', u'☃', None),
    (b'\xe2\x98\x83', u'☃', u'☃'),
])
def test_text_primitive(args):
    # workaround for pytest-dev/pytest#1086 until pytest 2.8.2 is released.
    s, prim_s, out_s = args
    if out_s is None:
        out_s = s

    assert TextTypeSpec.to_primitive(s) == prim_s
    assert TextTypeSpec.from_primitive(prim_s) == out_s


def test_validate():
    spec = TextTypeSpec
    spec.validate('foo')

    with pytest.raises(TypeError):
        spec.validate(1)
