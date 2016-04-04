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
The types of messages envelopes supported by Thrift.

.. py:data:: CALL
    :annotation: = 1

    An outgoing call to a specific method.

    ``Message.body`` is a struct containing the request arguments.

.. py:data:: REPLY
    :annotation: = 2

    A response to a ``CALL`` message.

    ``Message.body`` is a union of the return value (with field ID 0) and the
    application exceptions that the message can raise.

.. py:data:: EXCEPTION
    :annotation: = 3

    An unexpected exception in response to a ``CALL`` message.

    ``Message.body`` is a struct representing the exception.

    Note that exceptions that are defined in the IDL are returned as part of
    the ``REPLY`` message. This message type is used for unexpected exceptions
    that were not defined in the IDL but which the server and client have
    agreed upon as standard exceptions that they both recognize.

.. py:data:: ONEWAY
    :annotation: = 4

    An outgoing request to a specific ``oneway`` method.

    ``Message.body`` is the same as a ``CALL`` message but no ``REPLY`` or
    ``EXCEPTION`` is expected in response.

.. versionadded:: 1.0
"""

from __future__ import absolute_import, unicode_literals, print_function

MESSAGE_TYPES = (CALL, REPLY, EXCEPTION, ONEWAY)


cpdef str name_of(int value):
    """Returns the name of the message type with the given value.

    Returns None if no such message type exists.
    """
    if value == CALL:
        return str('CALL')
    elif value == REPLY:
        return str('REPLY')
    elif value == EXCEPTION:
        return str('EXCEPTION')
    elif value == ONEWAY:
        return str('ONEWAY')
    else:
        return None
