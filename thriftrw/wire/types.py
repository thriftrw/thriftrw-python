from __future__ import absolute_import, unicode_literals, print_function

from collections import namedtuple

_TType = namedtuple(
    '_TType',
    'BOOL BYTE DOUBLE I16 I32 I64 BINARY STRUCT MAP SET LIST'
)

#: Mapping of value type to code used by Thrift to represent that type.
#:
#: Usually callers won't need to use this directly.
TType = _TType(
    BOOL=2,
    BYTE=3,
    DOUBLE=4,
    I16=6,
    I32=8,
    I64=10,
    BINARY=11,
    STRUCT=12,
    MAP=13,
    SET=14,
    LIST=15,
)
