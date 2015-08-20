# coding=utf-8

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

from thriftrw.compile import spec
from thriftrw.wire import TType

from tests.util.value import *  # noqa


@pytest.mark.parametrize('t_spec, value, obj', [
    (spec.BoolTypeSpec, vbool(True), True),
    (spec.BoolTypeSpec, vbool(False), False),

    (spec.ByteTypeSpec, vbyte(42), 42),
    (spec.DoubleTypeSpec, vdouble(1.0138910), 1.0138910),
    (spec.I16TypeSpec, vi16(13907), 13907),
    (spec.I32TypeSpec, vi32(198314), 198314),
    (spec.I64TypeSpec, vi64(13814081), 13814081),

    (spec.BinaryTypeSpec, vbinary(''), b''),
    (spec.BinaryTypeSpec, vbinary('hello'), b'hello'),

    (spec.TextTypeSpec, vbinary(b'\xe2\x98\x83'), u'☃'),

    (spec.ListTypeSpec(spec.I16TypeSpec), vlist(TType.I16), []),
    (spec.ListTypeSpec(spec.ByteTypeSpec),
     vlist(TType.BYTE, vbyte(1), vbyte(2), vbyte(3)),
     [1, 2, 3]),
])
def test_primitive_wire_conversion(t_spec, value, obj):
    assert not t_spec.is_reference
    assert value == t_spec.to_wire(obj)
    assert obj == t_spec.from_wire(value)


@pytest.mark.parametrize('t_spec, pairs, obj', [
    (spec.MapTypeSpec(spec.TextTypeSpec, spec.I32TypeSpec), [], {}),
    (
        spec.MapTypeSpec(spec.TextTypeSpec, spec.I32TypeSpec),
        [
            (vbinary(b'a'), vi32(1)),
            (vbinary(b'b'), vi32(2)),
            (vbinary(b'c'), vi32(3)),
            (vbinary(b'\xe2\x98\x83'), vi32(4)),
        ],
        {
            u'a': 1,
            u'b': 2,
            u'c': 3,
            u'☃': 4,
        }
    )

])
def test_map_wire_conversion(t_spec, pairs, obj):
    assert not t_spec.is_reference
    ktype = t_spec.kspec.ttype_code
    vtype = t_spec.vspec.ttype_code

    assert t_spec.from_wire(vmap(ktype, vtype, *pairs)) == obj

    value = t_spec.to_wire(obj)
    assert ktype == value.key_ttype
    assert vtype == value.value_ttype
    assert set(pairs) == set(value.pairs)


def test_map_from_wire_duplicate_keys():
    mspec = spec.MapTypeSpec(spec.I16TypeSpec, spec.I32TypeSpec)
    result = mspec.from_wire(vmap(
        TType.I16, TType.I32,
        (vi16(0), vi32(1)),
        (vi16(2), vi32(3)),
        (vi16(4), vi32(5)),
        (vi16(0), vi32(6)),
    ))

    assert {0: 6, 2: 3, 4: 5} == result


def test_function_spec_transform():
    fspec = spec.FunctionSpec(
        'doSomething', spec.I16TypeSpec, spec.ByteTypeSpec
    )
    fspec.transform_types(spec.SetTypeSpec)

    assert fspec.args_spec.__class__ == spec.SetTypeSpec
    assert fspec.result_spec.__class__ == spec.SetTypeSpec
    assert fspec.args_spec.vspec == spec.I16TypeSpec
    assert fspec.result_spec.vspec == spec.ByteTypeSpec


def test_service_spec_transform():
    refs = {
        'getFooArgs': spec.BinaryTypeSpec,
        'getFooResult': spec.I16TypeSpec,
        'setBarArgs': spec.DoubleTypeSpec,
        'setBarResult': spec.TextTypeSpec,
    }

    sspec = spec.ServiceSpec(
        'MyService',
        [
            spec.FunctionSpec(
                'getFoo',
                spec.TypeReference('getFooArgs', 0),
                spec.TypeReference('getFooResult', 0),
            ),
            spec.FunctionSpec(
                'setBar',
                spec.TypeReference('setBarArgs', 0),
                spec.TypeReference('setBarResult', 0),
            )
        ],
        None
    )

    sspec.transform_types(lambda ref: refs[ref.name])

    assert sspec.functions[0].args_spec == spec.BinaryTypeSpec
    assert sspec.functions[0].result_spec == spec.I16TypeSpec

    assert sspec.functions[1].args_spec == spec.DoubleTypeSpec
    assert sspec.functions[1].result_spec == spec.TextTypeSpec
