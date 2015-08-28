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
Types
-----

.. autodata:: thriftrw.wire.TType
    :annotation:

Value
-----

.. autoclass:: thriftrw.wire.Value
    :members:

.. autoclass:: thriftrw.wire.ValueVisitor
    :members:

Value Types
~~~~~~~~~~~

.. autoclass:: thriftrw.wire.BoolValue

.. autoclass:: thriftrw.wire.ByteValue

.. autoclass:: thriftrw.wire.DoubleValue

.. autoclass:: thriftrw.wire.I16Value

.. autoclass:: thriftrw.wire.I32Value

.. autoclass:: thriftrw.wire.I64Value

.. autoclass:: thriftrw.wire.BinaryValue

.. autoclass:: thriftrw.wire.FieldValue

.. autoclass:: thriftrw.wire.StructValue

.. autoclass:: thriftrw.wire.MapValue

.. autoclass:: thriftrw.wire.SetValue

.. autoclass:: thriftrw.wire.ListValue
"""
from __future__ import absolute_import, unicode_literals, print_function

from .ttype import TType

from .value import (
    Value,
    BoolValue,
    ByteValue,
    DoubleValue,
    I16Value,
    I32Value,
    I64Value,
    BinaryValue,
    FieldValue,
    StructValue,
    MapValue,
    SetValue,
    ListValue,
    ValueVisitor,
)

__all__ = [
    'TType',

    # Value
    'Value',
    'BoolValue',
    'ByteValue',
    'DoubleValue',
    'I16Value',
    'I32Value',
    'I64Value',
    'BinaryValue',
    'FieldValue',
    'StructValue',
    'MapValue',
    'SetValue',
    'ListValue',
    'ValueVisitor',
]
