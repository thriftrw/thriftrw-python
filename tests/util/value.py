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

"""
This module provides helpers to construct Value objects for tests.
"""
from __future__ import absolute_import, unicode_literals, print_function

import six

from thriftrw.wire import value


vbool = value.BoolValue
vbyte = value.ByteValue
vi16 = value.I16Value
vi32 = value.I32Value
vi64 = value.I64Value
vdouble = value.DoubleValue


def vbinary(s):
    return value.BinaryValue(six.binary_type(s))


def vstruct(*fields):
    return value.StructValue([value.FieldValue(*args) for args in fields])


def vlist(typ, *items):
    return value.ListValue(typ, list(items))


def vmap(ktype, vtype, *items):
    return value.MapValue(ktype, vtype, list(items))


def vset(vtype, *items):
    return value.SetValue(vtype, list(items))


__all__ = [
    'vbool', 'vbyte', 'vi16', 'vi32', 'vi64', 'vdouble', 'vbinary', 'vstruct',
    'vlist', 'vmap', 'vset'
]
