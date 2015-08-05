"""
A parser for Thrift IDL files.

Parser
------

Adapted from ``thriftpy.parser``.

.. autoclass:: Parser
    :members:

.. autoclass:: ThriftParserError

AST
---

.. autoclass:: Program

Headers
~~~~~~~

.. autoclass:: Include

.. autoclass:: Namespace

Definitions
~~~~~~~~~~~

.. autoclass:: Const

.. autoclass:: Typedef

.. autoclass:: Enum

.. autoclass:: EnumItem

.. autoclass:: Struct

.. autoclass:: Union

.. autoclass:: Exc

.. autoclass:: Service

.. autoclass:: Function

.. autoclass:: Field

Types
~~~~~

.. autoclass:: BoolType

.. autoclass:: ByteType

.. autoclass:: I16Type

.. autoclass:: I32Type

.. autoclass:: I64Type

.. autoclass:: DoubleType

.. autoclass:: StringType

.. autoclass:: BinaryType

.. autoclass:: MapType

.. autoclass:: SetType

.. autoclass:: ListType

.. autoclass:: DefinedType

Constants
~~~~~~~~~

.. autoclass:: ConstValue

.. autoclass:: ConstReference

Annotations
~~~~~~~~~~~

.. autoclass:: Annotation

"""
from __future__ import absolute_import, unicode_literals, print_function

from .ast import *  # noqa
from .exceptions import *  # noqa
from .parser import Parser  # noqa
