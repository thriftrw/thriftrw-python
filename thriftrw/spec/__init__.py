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

from .base import TypeSpec
from .enum import EnumTypeSpec
from .list import ListTypeSpec
from .map import MapTypeSpec
from .set import SetTypeSpec
from .struct import StructTypeSpec, FieldSpec
from .exc import ExceptionTypeSpec
from .union import UnionTypeSpec
from .service import ServiceSpec, FunctionSpec
from .typedef import TypedefTypeSpec
from .reference import TypeReference
from .primitive import (
    BoolTypeSpec,
    ByteTypeSpec,
    DoubleTypeSpec,
    I16TypeSpec,
    I32TypeSpec,
    I64TypeSpec,
    BinaryTypeSpec,
    TextTypeSpec,
)


__all__ = [
    'TypeSpec',

    # Primitives
    'BoolTypeSpec',
    'ByteTypeSpec',
    'DoubleTypeSpec',
    'I16TypeSpec',
    'I32TypeSpec',
    'I64TypeSpec',
    'BinaryTypeSpec',
    'TextTypeSpec',

    # Containers
    'ListTypeSpec',
    'MapTypeSpec',
    'SetTypeSpec',

    # Custom types

    'EnumTypeSpec',

    'ExceptionTypeSpec',
    'StructTypeSpec',
    'UnionTypeSpec',
    'FieldSpec',

    'ServiceSpec',
    'FunctionSpec',

    'TypeReference',
    'TypedefTypeSpec',
]
