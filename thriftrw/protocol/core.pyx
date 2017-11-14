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

from libc.stdint cimport (
    int8_t,
    int16_t,
    int32_t,
    int64_t,
)

from thriftrw.wire cimport ttype
from thriftrw.wire.value cimport Value, ValueVisitor
from thriftrw.wire.message cimport Message


__all__ = ['Protocol']


cdef class MessageHeader(object):

    def __cinit__(MessageHeader self, bytes name, int8_t type, int32_t seqid):
        self.name = name
        self.type = type
        self.seqid = seqid

    def __str__(self):
        return 'MessageHeader(%r, %r, %r)' % (
            self.name, self.seqid, ttype.name_of(self.type)
        )

    def __repr__(self):
        return str(self)


cdef class ProtocolWriter(object):

    cdef void write_value(self, Value value) except *:
        value.apply(_ValueWriter(self))

    cdef void write_bool(self, bint value) except *: pass
    cdef void write_byte(self, int8_t value) except *: pass
    cdef void write_double(self, double value) except *: pass
    cdef void write_i16(self, int16_t value) except *: pass
    cdef void write_i32(self, int32_t value) except *: pass
    cdef void write_i64(self, int64_t value) except *: pass
    cdef void write_binary(self, char* value, int32_t length) except *: pass
    cdef void write_struct_begin(self) except *: pass
    cdef void write_field_begin(self, FieldHeader header) except *: pass
    cdef void write_field_end(self) except *: pass
    cdef void write_struct_end(self) except *: pass
    cdef void write_map_begin(self, MapHeader header) except *: pass
    cdef void write_map_end(self) except *: pass
    cdef void write_set_begin(self, SetHeader header) except *: pass
    cdef void write_set_end(self) except *: pass
    cdef void write_list_begin(self, ListHeader header) except *: pass
    cdef void write_list_end(self) except *: pass
    cdef void write_message_begin(self, MessageHeader header) except *: pass
    cdef void write_message_end(self) except *: pass


cdef class ProtocolReader:

    # Skip

    cdef void skip(self, int typ) except *: pass
    cdef void skip_binary(self) except *: pass
    cdef void skip_map(self) except *: pass
    cdef void skip_list(self) except *: pass
    cdef void skip_set(self) except *: pass
    cdef void skip_struct(self) except *: pass

    # Primitives

    cdef bint read_bool(self) except *: pass
    cdef int8_t read_byte(self) except *: pass
    cdef double read_double(self) except *: pass
    cdef int16_t read_i16(self) except *: pass
    cdef int32_t read_i32(self) except *: pass
    cdef int64_t read_i64(self) except *: pass
    cdef bytes read_binary(self): pass

    # Structs

    cdef void read_struct_begin(self) except *: pass
    cdef FieldHeader read_field_begin(self) except *:
        """Parse the next three bytes as a FieldHeader object.

        :return: FieldHeader with type and id set to -1 if a struct end is found.
        """
        pass
    cdef void read_field_end(self) except *: pass
    cdef void read_struct_end(self) except *: pass

    # Containers

    cdef MapHeader read_map_begin(self) except *: pass
    cdef void read_map_end(self) except *: pass

    cdef SetHeader read_set_begin(self) except *: pass
    cdef void read_set_end(self) except *: pass

    cdef ListHeader read_list_begin(self) except *: pass
    cdef void read_list_end(self) except *: pass

    # Messages

    cdef MessageHeader read_message_begin(self): pass
    cdef void read_message_end(self) except *: pass


cdef class Protocol(object):
    """Base class for all protocol implementations.

    .. versionchanged:: 1.0

        Removed ``dumps`` and ``loads`` methods and added
        ``serialize_message`` and ``deserialize_message``.
    """

    cpdef ProtocolReader reader(self, ReadBuffer buff):
        raise NotImplementedError

    cpdef ProtocolWriter writer(self, WriteBuffer buff):
        raise NotImplementedError

    cpdef bytes serialize_value(self, Value value):
        """Serialize the given ``Value``.

        :param ~thriftrw.wire.Value value:
            Value to serialize.
        :returns:
            Serialized value.
        """
        cdef WriteBuffer buff = WriteBuffer()
        cdef ProtocolWriter writer = self.writer(buff)
        writer.write_value(value)
        return buff.value

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
        cdef WriteBuffer buff = WriteBuffer()
        cdef ProtocolWriter writer = self.writer(buff)
        cdef MessageHeader header = MessageHeader(
            message.name,
            message.message_type,
            message.seqid,
        )

        writer.write_message_begin(header)
        writer.write_value(message.body)
        writer.write_message_end()

        return buff.value

    cpdef Message deserialize_message(self, bytes s):
        """Deserialize a ``Message``.

        :param s:
            Bytes to decode
        :returns:
            Parsed :py:class:`~thriftrw.wire.Message` containing a
            :py:class:`~thriftrw.wire.Value` in its body.
        """

cdef class _ValueWriter(ValueVisitor):

    def __cinit__(_ValueWriter self, ProtocolWriter writer):
        self.writer = writer

    cdef object visit_bool(self, bint value):
        self.writer.write_bool(value)

    cdef object visit_byte(self, int8_t value):
        self.writer.write_byte(value)

    cdef object visit_double(self, double value):
        self.writer.write_double(value)

    cdef object visit_i16(self, int16_t value):
        self.writer.write_i16(value)

    cdef object visit_i32(self, int32_t value):
        self.writer.write_i32(value)

    cdef object visit_i64(self, int64_t value):
        self.writer.write_i64(value)

    cdef object visit_binary(self, bytes value):
        self.writer.write_binary(value, len(value))

    cdef object visit_struct(self, list fields):
        self.writer.write_struct_begin()
        for f in fields:
            self.writer.write_field_begin(FieldHeader(f.ttype, f.id))
            f.value.apply(self)
            self.writer.write_field_end()
        self.writer.write_struct_end()

    cdef object visit_map(self, int8_t key_ttype, int8_t value_ttype,
                          list pairs):
        cdef MapHeader header = MapHeader(key_ttype, value_ttype, len(pairs))
        self.writer.write_map_begin(header)
        for item in pairs:
            item.key.apply(self)
            item.value.apply(self)
        self.writer.write_map_end()

    cdef object visit_set(self, int8_t value_ttype, list values):
        cdef SetHeader header = SetHeader(value_ttype, len(values))
        self.writer.write_set_begin(header)
        for value in values:
            value.apply(self)
        self.writer.write_set_end()

    cdef object visit_list(self, int8_t value_ttype, list values):
        cdef ListHeader header = ListHeader(value_ttype, len(values))
        self.writer.write_list_begin(header)
        for value in values:
            value.apply(self)
        self.writer.write_list_end()
