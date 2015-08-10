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
