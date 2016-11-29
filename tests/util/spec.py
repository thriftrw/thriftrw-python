from thriftrw.spec.list import ListTypeSpec
from thriftrw.spec.map import MapTypeSpec
from thriftrw.spec.struct import StructTypeSpec
from thriftrw.spec.set import SetTypeSpec
from thriftrw.idl import Parser
from thriftrw.compile.scope import Scope


parse_struct = Parser(start='struct', silent=True).parse


def sstruct(fields=""):
    """This helper creates a mock spec for sstruct """
    struct_ast = parse_struct('struct RefStruct { %s }' % fields)
    spec = StructTypeSpec.compile(struct_ast)
    spec.link(Scope("test"))
    return spec


def smap(key, value):
    return MapTypeSpec(key, value)


def sset(value):
    return SetTypeSpec(value)


def slist(value):
    return ListTypeSpec(value)
