# Copyright (c) 2016 Uber Technologies, Inc.
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
.. autoclass:: ThriftError
    :members:

.. autoclass:: ThriftParserError
    :members:

.. autoclass:: ThriftCompilerError
    :members:

.. autoclass:: ThriftProtocolError
    :members:

.. autoclass:: EndOfInputError
    :members:

.. autoclass:: UnknownExceptionError
    :members:
"""
from __future__ import absolute_import, unicode_literals, print_function


class ThriftError(Exception):
    """Base class for all exceptions raised by thriftrw."""


class ThriftParserError(ThriftError):
    """Exception raised by the parser or lexer in case of errors."""


class ThriftCompilerError(ThriftError):
    """Exception raised during IDL compilation."""


class ThriftProtocolError(ThriftError):
    """Exceptions raised by Protocol implementations for errors encountered
    during serialization or deserialization.
    """


class EndOfInputError(ThriftProtocolError):
    """The input was shorter than expected."""


class UnknownExceptionError(ThriftError):
    """We parsed an unknown exception in a function response."""

    def __init__(self, message, thrift_response=None):
        super(UnknownExceptionError, self).__init__(message)
        self.thrift_response = thrift_response

    def __str__(self):
        return 'UnknownExceptionError(%s, thrift_response=%r)' % (
            super(UnknownExceptionError, self).__str__(),
            self.thrift_response,
        )

    __repr__ = __str__
