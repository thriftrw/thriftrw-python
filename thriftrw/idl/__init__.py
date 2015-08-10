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

.. autoclass:: PrimitiveType

.. autoclass:: MapType

.. autoclass:: SetType

.. autoclass:: ListType

.. autoclass:: DefinedType

Constants
~~~~~~~~~

.. autoclass:: ConstPrimitiveValue

.. autoclass:: ConstReference

Annotations
~~~~~~~~~~~

.. autoclass:: Annotation

Exceptions
----------

.. autoclass:: ThriftParserError
    :members:

"""
from __future__ import absolute_import, unicode_literals, print_function

from .ast import *  # noqa
from .exceptions import *  # noqa
from .parser import Parser  # noqa
