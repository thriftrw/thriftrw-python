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

import abc


__all__ = ['Protocol']


class Protocol(object):
    """Base class for all protocol implementations."""

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def dump(self, value):
        """Serialize the given ``Value``.

        :param ~thriftrw.wire.Value value:
            Value to serialize.
        :returns:
            Serialized value.
        """

    @abc.abstractmethod
    def load(self, typ, s):
        """Parse a ``Value`` of the given type.

        :param ~thriftrw.wire.TType typ:
            Type code of the value to parse.
        :param s:
            Bytes to decode.
        :returns:
            Parsed :py:class:`~thriftrw.wire.Value`.
        """

    # TODO do we care about Message envelopes?
