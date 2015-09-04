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
Specs
-----

Specs represent compiled ASTs and act as the *specification* of behavior for
the types or values they represent. All specs have a ``name`` and may have a
``surface`` attribute which, if not None, is exposed in the generated module
at the top-level.

.. autoclass:: thriftrw.spec.TypeSpec
    :members:

Native types
~~~~~~~~~~~~

.. autodata:: thriftrw.spec.BoolTypeSpec
    :annotation:

.. autodata:: thriftrw.spec.ByteTypeSpec
    :annotation:

.. autodata:: thriftrw.spec.DoubleTypeSpec
    :annotation:

.. autodata:: thriftrw.spec.I16TypeSpec
    :annotation:

.. autodata:: thriftrw.spec.I32TypeSpec
    :annotation:

.. autodata:: thriftrw.spec.I64TypeSpec
    :annotation:

.. autodata:: thriftrw.spec.BinaryTypeSpec
    :annotation:

.. autodata:: thriftrw.spec.TextTypeSpec
    :annotation:

.. autoclass:: thriftrw.spec.ListTypeSpec
    :members:

.. autoclass:: thriftrw.spec.MapTypeSpec
    :members:

.. autoclass:: thriftrw.spec.SetTypeSpec
    :members:

Custom Types
~~~~~~~~~~~~

.. autoclass:: thriftrw.spec.EnumTypeSpec
    :members:

.. autoclass:: thriftrw.spec.StructTypeSpec
    :members:

.. autoclass:: thriftrw.spec.ExceptionTypeSpec
    :members:

.. autoclass:: thriftrw.spec.UnionTypeSpec
    :members:

.. autoclass:: thriftrw.spec.FieldSpec
    :members:

.. autoclass:: thriftrw.spec.TypedefTypeSpec
    :members:

Services
~~~~~~~~

.. autoclass:: thriftrw.spec.ServiceSpec
    :members:

.. autoclass:: thriftrw.spec.ServiceFunction
    :members:

.. autoclass:: thriftrw.spec.FunctionSpec
    :members:

.. autoclass:: thriftrw.spec.FunctionResultSpec
    :members:

Constants
~~~~~~~~~

.. autoclass:: thriftrw.spec.ConstSpec
    :members:
"""
from __future__ import absolute_import, unicode_literals, print_function

from .base import TypeSpec
from .const import ConstSpec
from .enum import EnumTypeSpec
from .list import ListTypeSpec
from .map import MapTypeSpec
from .set import SetTypeSpec
from .struct import StructTypeSpec, FieldSpec
from .exc import ExceptionTypeSpec
from .union import UnionTypeSpec
from .typedef import TypedefTypeSpec
from .service import (
    ServiceSpec,
    FunctionSpec,
    FunctionResultSpec,
    ServiceFunction,
)
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
    # Types
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

    'TypedefTypeSpec',

    # Services
    'ServiceSpec',
    'FunctionSpec',
    'FunctionResultSpec',
    'ServiceFunction',

    # Constants
    'ConstSpec',
]
