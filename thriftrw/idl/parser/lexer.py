from __future__ import absolute_import, unicode_literals, print_function

import six
from ply import lex

from .exceptions import ThriftLexerError


THRIFT_KEYWORDS = (
    'namespace',
    'include',
    'void',
    'bool',
    'byte',
    'i16',
    'i32',
    'i64',
    'double',
    'string',
    'binary',
    'map',
    'list',
    'set',
    'oneway',
    'typedef',
    'struct',
    'union',
    'exception',
    'extends',
    'throws',
    'service',
    'enum',
    'const',
    'required',
    'optional',
)

class Lexer(object):
    """Lexer for Thrift IDL files.
    
    Adapted from thriftpy.parser.lexer."""

    literals = ':;,=*{}()<>[]'

    tokens = (
        'BOOLCONSTANT',
        'INTCONSTANT',
        'DUBCONSTANT',
        'LITERAL',
        'IDENTIFIER',
    ) + tuple(map(six.text_type.upper, THRIFT_KEYWORDS))


    t_ignore = ' \t\r'   # whitespace

    def t_error(self, t):
        raise ThriftLexerError(
            'Illegal characher %r at line %d' % (t.value[0], t.lineno)
        )

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_ignore_SILLYCOMM(self, t):
        r'\/\*\**\*\/'
        t.lexer.lineno += t.value.count('\n')

    def t_ignore_MULTICOMM(self, t):
        r'\/\*[^*]\/*([^*/]|[^*]\/|\*[^/])*\**\*\/'
        t.lexer.lineno += t.value.count('\n')

    def t_ignore_DOCTEXT(self, t):
        r'\/\*\*([^*/]|[^*]\/|\*[^/])*\**\*\/'
        t.lexer.lineno += t.value.count('\n')

    def t_ignore_UNIXCOMMENT(self, t):
        r'\#[^\n]*'

    def t_ignore_COMMENT(self, t):
        r'\/\/[^\n]*'

    def t_BOOLCONSTANT(self, t):
        r'true|false'
        t.value = t.value == 'true'
        return t

    def t_DUBCONSTANT(self, t):
        r'-?\d+\.\d*(e-?\d+)?'
        t.value = float(t.value)
        return t

    def t_HEXCONSTANT(self, t):
        r'0x[0-9A-Fa-f]+'
        t.value = int(t.value, 16)
        t.type = 'INTCONSTANT'
        return t

    def t_INTCONSTANT(self, t):
        r'[+-]?[0-9]+'
        t.value = int(t.value)
        return t

    def t_LITERAL(self, t):
        r'(\"([^\\\n]|(\\.))*?\")|\'([^\\\n]|(\\.))*?\''
        s = t.value[1:-1]
        maps = {
            't': '\t',
            'r': '\r',
            'n': '\n',
            '\\': '\\',
            '\'': '\'',
            '"': '\"'
        }
        i = 0
        length = len(s)
        val = ''
        while i < length:
            if s[i] == '\\':
                i += 1
                if s[i] in maps:
                    val += maps[s[i]]
                else:
                    msg = 'Cannot escape character: %s' % s[i]
                    raise ThriftLexerError(msg)
            else:
                val += s[i]
            i += 1

        t.value = val
        return t

    def t_IDENTIFIER(self, t):
        r'[a-zA-Z_](\.[a-zA-Z_0-9]|[a-zA-Z_0-9])*'

        if t.value in THRIFT_KEYWORDS:
            # Not an identifier after all.
            t.type = t.value.upper()

        return t

    # END LEXER SPECIFICATION ##########################################

    @classmethod
    def build(cls, **kwargs):
        # For now, we just return the Ply lexer. We can customize it later.
        return lex.lex(module=cls(), **kwargs)
