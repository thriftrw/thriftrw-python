import re

from thriftrw.spec.list import ListTypeSpec
from thriftrw.spec.map import MapTypeSpec
from thriftrw.spec.struct import StructTypeSpec
from thriftrw.spec.union import UnionTypeSpec
from thriftrw.spec.field import FieldSpec
from thriftrw.spec.set import SetTypeSpec
from thriftrw.idl import Parser
from thriftrw.compile.scope import Scope


parse = Parser(start='struct', silent=True).parse


def sstruct(fields):
    struct_ast = parse('struct RefStruct {{ {} }}'.format(fields))
    spec = StructTypeSpec.compile(struct_ast)
    spec.link(Scope("test"))
    return spec


def smap(key, value):
    return MapTypeSpec(key, value)


def sunion(*fields):
    return UnionTypeSpec("test", list(fields))


def sf(id, spec, name=None, required=False, default_value=None):
    if name is None:
        name = re.sub("[^a-zA-Z_0-9]+", "", str(spec) + str(id))

    return FieldSpec(id, name, spec, required, default_value)


def sset(value):
    return SetTypeSpec(value)


def slist(value):
    return ListTypeSpec(value)
