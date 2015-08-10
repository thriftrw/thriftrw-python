from __future__ import absolute_import, unicode_literals, print_function


class ThriftProtocolError(Exception):
    # TODO all exceptions raised by this library must havea common parent.
    pass


class EndOfInputError(ThriftProtocolError):
    pass
