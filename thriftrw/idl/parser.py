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

from collections import deque

from ply import yacc

from . import ast
from .lexer import Lexer
from .exceptions import ThriftParserError


__all__ = ['Parser']


class ParserSpec(object):
    """Parser specification for Thrift IDL files.

    Adapted from ``thriftpy.parser.parser``."""

    tokens = Lexer.tokens

    def p_error(self, p):
        if p is None:
            raise ThriftParserError('Grammer error at EOF')
        raise ThriftParserError(
            'Grammar error %r at line %d' % (p.value, p.lineno)
        )

    def p_start(self, p):
        '''start : header definition'''
        p[0] = ast.Program(headers=p[1], definitions=p[2])

    def p_header(self, p):
        '''header : header_unit_ header
                  |'''
        self._parse_seq(p)

    def p_header_unit_(self, p):
        '''header_unit_ : header_unit ';'
                        | header_unit'''
        p[0] = p[1]

    def p_header_unit(self, p):
        '''header_unit : include
                       | namespace'''
        p[0] = p[1]

    def p_include(self, p):
        '''include : INCLUDE LITERAL'''
        p[0] = ast.Include(path=p[2], lineno=p.lineno(1))

    def p_namespace(self, p):
        '''namespace : NAMESPACE namespace_scope IDENTIFIER'''
        p[0] = ast.Namespace(scope=p[2], name=p[3], lineno=p.lineno(1))

    def p_namespace_scope(self, p):
        '''namespace_scope : '*'
                           | IDENTIFIER'''
        p[0] = p[1]

    def p_sep(self, p):
        '''sep : ','
               | ';'
        '''

    def p_definition(self, p):
        '''definition : definition_unit_ definition
                      |'''
        self._parse_seq(p)

    def p_definition_unit_(self, p):
        '''definition_unit_ : definition_unit ';'
                            | definition_unit'''
        p[0] = p[1]

    def p_definition_unit(self, p):
        '''definition_unit : const
                           | ttype
        '''
        p[0] = p[1]

    def p_const(self, p):
        '''const : CONST field_type IDENTIFIER '=' const_value
                 | CONST field_type IDENTIFIER '=' const_value sep'''
        p[0] = ast.Const(
            name=p[3],
            value_type=p[2],
            value=p[5],
            lineno=p.lineno(3),
        )

    def p_const_value(self, p):
        '''const_value : const_value_native
                       | const_ref'''
        p[0] = p[1]

    def p_const_value_native(self, p):
        '''const_value_native : const_value_primitive
                              | const_list
                              | const_map'''
        p[0] = p[1]

    def p_const_value_primitive(self, p):
        '''const_value_primitive : INTCONSTANT
                                 | DUBCONSTANT
                                 | LITERAL
                                 | BOOLCONSTANT'''
        p[0] = ast.ConstPrimitiveValue(p[1], lineno=p.lineno(1))

    def p_const_list(self, p):
        '''const_list : '[' const_list_seq ']' '''
        p[0] = ast.ConstList(list(p[2]), p.lineno(2))

    def p_const_list_seq(self, p):
        '''const_list_seq : const_value sep const_list_seq
                          | const_value const_list_seq
                          |'''
        self._parse_seq(p)

    def p_const_map(self, p):
        '''const_map : '{' const_map_seq '}' '''
        p[0] = ast.ConstMap(dict(p[2]), p.lineno(2))

    def p_const_map_seq(self, p):
        '''const_map_seq : const_map_item sep const_map_seq
                         | const_map_item const_map_seq
                         |'''
        self._parse_seq(p)

    def p_const_map_item(self, p):
        '''const_map_item : const_value ':' const_value '''
        p[0] = (p[1], p[3])

    def p_const_ref(self, p):
        '''const_ref : IDENTIFIER'''
        p[0] = ast.ConstReference(p[1], lineno=p.lineno(1))

    def p_ttype(self, p):
        '''ttype : typedef
                 | enum
                 | struct
                 | union
                 | exception
                 | service'''
        p[0] = p[1]

    def p_typedef(self, p):
        '''typedef : TYPEDEF field_type IDENTIFIER annotations'''
        p[0] = ast.Typedef(
            name=p[3], target_type=p[2], annotations=p[4], lineno=p.lineno(3)
        )

    def p_enum(self, p):  # noqa
        '''enum : ENUM IDENTIFIER '{' enum_seq '}' annotations'''
        p[0] = ast.Enum(
            name=p[2], items=p[4], annotations=p[6], lineno=p.lineno(2)
        )

    def p_enum_seq(self, p):
        '''enum_seq : enum_item sep enum_seq
                    | enum_item enum_seq
                    |'''
        self._parse_seq(p)

    def p_enum_item(self, p):
        '''enum_item : IDENTIFIER '=' INTCONSTANT annotations
                     | IDENTIFIER annotations'''
        if len(p) == 5:
            p[0] = ast.EnumItem(
                name=p[1], value=p[3], annotations=p[4], lineno=p.lineno(1)
            )
        else:
            p[0] = ast.EnumItem(
                name=p[1], value=None, annotations=p[2], lineno=p.lineno(1)
            )

    def p_struct(self, p):
        '''struct : STRUCT IDENTIFIER '{' field_seq '}' annotations'''
        p[0] = ast.Struct(
            name=p[2], fields=p[4], annotations=p[6], lineno=p.lineno(2)
        )

    def p_union(self, p):
        '''union : UNION IDENTIFIER '{' field_seq '}' annotations'''
        p[0] = ast.Union(
            name=p[2], fields=p[4], annotations=p[6], lineno=p.lineno(2)
        )

    def p_exception(self, p):
        '''exception : EXCEPTION IDENTIFIER '{' field_seq '}' annotations'''
        p[0] = ast.Exc(
            name=p[2], fields=p[4], annotations=p[6], lineno=p.lineno(2)
        )

    def p_service(self, p):
        '''service : SERVICE IDENTIFIER '{' function_seq '}' annotations
                   | SERVICE IDENTIFIER EXTENDS IDENTIFIER \
                     '{' function_seq '}' annotations
        '''

        if len(p) == 7:
            p[0] = ast.Service(
                name=p[2],
                functions=p[4],
                parent=None,
                annotations=p[6],
                lineno=p.lineno(2),
            )
        else:
            p[0] = ast.Service(
                name=p[2],
                functions=p[6],
                parent=p[4],
                annotations=p[8],
                lineno=p.lineno(2),
            )

    def p_oneway(self, p):
        '''oneway : ONEWAY
                  |'''
        p[0] = len(p) > 1

    def p_function(self, p):
        '''function : oneway function_type IDENTIFIER '(' field_seq ')' \
                      throws annotations '''
        p[0] = ast.Function(
            name=p[3],
            parameters=p[5],
            return_type=p[2],
            exceptions=p[7],
            oneway=p[1],
            annotations=p[8],
            lineno=p.lineno(3),
        )

    def p_function_seq(self, p):
        '''function_seq : function sep function_seq
                        | function function_seq
                        |'''
        self._parse_seq(p)

    def p_throws(self, p):
        '''throws : THROWS '(' field_seq ')'
                  |'''
        if len(p) == 5:
            p[0] = p[3]
        else:
            p[0] = deque()

    def p_function_type(self, p):
        '''function_type : field_type
                         | VOID'''
        if p[1] == 'void':
            p[0] = None
        else:
            p[0] = p[1]

    def p_field_seq(self, p):
        '''field_seq : field sep field_seq
                     | field field_seq
                     |'''
        self._parse_seq(p)

    def p_field(self, p):
        '''field : field_id field_req field_type IDENTIFIER annotations
                 | field_id field_req field_type IDENTIFIER '=' const_value \
                   annotations'''

        if len(p) == 8:
            default = p[6]
            annotations = p[7]
        else:
            default = None
            annotations = p[5]

        p[0] = ast.Field(
            id=p[1],
            name=p[4],
            field_type=p[3],
            requiredness=p[2],
            default=default,
            annotations=annotations,
            lineno=p.lineno(4),
        )

    def p_field_id(self, p):
        '''field_id : INTCONSTANT ':'
                    | '''
        if len(p) == 3:

            if p[1] == 0:
                # Prevent users from ever using field ID 0. It's reserved for
                # internal use only.
                raise ThriftParserError(
                    'Line %d: Field ID 0 is reserved for internal use.'
                    % p.lineno(1)
                )

            p[0] = p[1]
        else:
            p[0] = None

    def p_field_req(self, p):
        '''field_req : REQUIRED
                     | OPTIONAL
                     |'''
        if len(p) == 2:
            p[0] = p[1] == 'required'
        else:
            p[0] = None  # don't have a default

    def p_field_type(self, p):
        '''field_type : ref_type
                      | definition_type'''
        p[0] = p[1]

    def p_ref_type(self, p):
        '''ref_type : IDENTIFIER'''
        p[0] = ast.DefinedType(p[1], lineno=p.lineno(1))

    def p_base_type(self, p):  # noqa
        '''base_type : BOOL annotations
                     | BYTE annotations
                     | I16 annotations
                     | I32 annotations
                     | I64 annotations
                     | DOUBLE annotations
                     | STRING annotations
                     | BINARY annotations'''

        p[0] = ast.PrimitiveType(p[1], p[2])

    def p_container_type(self, p):
        '''container_type : map_type
                          | list_type
                          | set_type'''
        p[0] = p[1]

    def p_map_type(self, p):
        '''map_type : MAP '<' field_type ',' field_type '>' annotations'''
        p[0] = ast.MapType(key_type=p[3], value_type=p[5], annotations=p[7])

    def p_list_type(self, p):
        '''list_type : LIST '<' field_type '>' annotations'''
        p[0] = ast.ListType(value_type=p[3], annotations=p[5])

    def p_set_type(self, p):
        '''set_type : SET '<' field_type '>' annotations'''
        p[0] = ast.SetType(value_type=p[3], annotations=p[5])

    def p_definition_type(self, p):
        '''definition_type : base_type
                           | container_type'''
        p[0] = p[1]

    def p_annotations(self, p):
        '''annotations : '(' annotation_seq ')'
                       |'''
        if len(p) == 1:
            p[0] = []
        else:
            p[0] = list(p[2])

    def p_annotation_seq(self, p):
        '''annotation_seq : annotation sep annotation_seq
                          | annotation annotation_seq
                          |'''
        self._parse_seq(p)

    def p_annotation(self, p):
        '''annotation : IDENTIFIER '=' LITERAL '''
        p[0] = ast.Annotation(p[1], p[3], lineno=p.lineno(1))

    def _parse_seq(self, p):
        """Helper to parse sequence rules.

        Sequence rules are in the form::

            foo : foo_item sep foo
                | foo_item foo
                |

        This function builds a deque of the items in-order.

        If the number of tokens doesn't match, an exception is raised.
        """
        # This basically says:
        #
        # - When you reach the end of the list, construct and return an empty
        #   deque.
        # - Otherwise, prepend to start of what you got from the parser.
        #
        # So this ends up constructing an in-order list.
        if len(p) == 4:
            p[3].appendleft(p[1])
            p[0] = p[3]
        elif len(p) == 3:
            p[2].appendleft(p[1])
            p[0] = p[2]
        elif len(p) == 1:
            p[0] = deque()
        else:
            raise ThriftParserError(
                'Wrong number of tokens received for expression at line %d'
                % p.lineno(1)
            )


class Parser(ParserSpec):
    """Parser for Thrift IDL files."""

    def __init__(self, **kwargs):
        if kwargs.pop('silent', False):
            kwargs['errorlog'] = yacc.NullLogger()

        kwargs.setdefault('debug', False)
        kwargs.setdefault('write_tables', False)
        self._parser = yacc.yacc(module=self, **kwargs)
        self._lexer = Lexer()

    def parse(self, input, **kwargs):
        """Parse the given input.

        :param input:
            String containing the text to be parsed.
        :raises ThriftParserError:
            For parsing errors.
        """
        return self._parser.parse(input, lexer=self._lexer, **kwargs)
