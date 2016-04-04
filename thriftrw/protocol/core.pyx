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

from __future__ import absolute_import, unicode_literals, print_function

from thriftrw.wire cimport ttype
from thriftrw.wire.value cimport Value
from thriftrw.wire.message cimport Message


__all__ = ['Protocol']


cdef class Protocol(object):
    """Base class for all protocol implementations.

    .. versionchanged:: 1.0

        Removed ``dumps`` and ``loads`` methods and added
        ``serialize_message`` and ``deserialize_message``.
    """

    cpdef bytes serialize_value(self, Value value):
        """Serialize the given ``Value``.

        :param ~thriftrw.wire.Value value:
            Value to serialize.
        :returns:
            Serialized value.
        """

    cpdef Value deserialize_value(self, int typ, bytes s):
        """Parse a ``Value`` of the given type.

        :param typ:
            Type code of the value to parse.
        :param s:
            Bytes to decode.
        :returns:
            Parsed :py:class:`~thriftrw.wire.Value`.
        :raises thriftrw.errors.ThriftProtocolError:
            If the object failed to deserialize.
        """

    cpdef bytes serialize_message(self, Message message):
        """Serialize a ``Message``.

        The message body must be a :py:class:`~thriftrw.wire.Value`.

        :param message:
            Message to serialize.
        :returns:
            Serialized message.
        """

    cpdef Message deserialize_message(self, bytes s):
        """Deserialize a ``Message``.

        :param s:
            Bytes to decode
        :returns:
            Parsed :py:class:`~thriftrw.wire.Message` containing a
            :py:class:`~thriftrw.wire.Value` in its body.
        """
