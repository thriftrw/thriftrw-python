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
from thriftrw.wire.message cimport Message

from thriftrw._buffer cimport ReadBuffer
from thriftrw._buffer cimport WriteBuffer
from thriftrw.wire.value cimport (
    Value,
    BoolValue,
    ByteValue,
    DoubleValue,
    I16Value,
    I32Value,
    I64Value,
    BinaryValue,
    FieldValue,
    StructValue,
    MapValue,
    MapItem,
    SetValue,
    ListValue,
    ValueVisitor,
)

from .core cimport (
    Protocol,
    ProtocolWriter,
    ProtocolReader,
    FieldHeader,
    MapHeader,
    SetHeader,
    ListHeader,
    MessageHeader,
)
from ..errors import EndOfInputError
from ..errors import ThriftProtocolError
from ._endian cimport (
    htobe16,
    htobe32,
    htobe64,
    be16toh,
    be32toh,
    be64toh,
)


cdef STRUCT_END_HEADER = FieldHeader(-1, -1)

cdef int8_t STRUCT_END = 0

cdef int32_t VERSION = 1

# Under strict mode, the version number is in most significant 16-bits of the
# 32-bit integer, and the most significant bit is set. This mask gets &-ed
# with the integer to get just the version number (it still needs to be
# shifted 16-bits to the right).
cdef int32_t VERSION_MASK = 0x7fff0000

# The least significant 8-bits of the 32-bit integer contain the type.
cdef int32_t TYPE_MASK = 0x000000ff


cdef class BinaryProtocolReader(ProtocolReader):
    """Parser for the binary protocol."""

    def __cinit__(self, ReadBuffer reader):
        """Initialize the reader.

        :param reader:
            File-like object with a ``read(num)`` method which returns
            *exactly* the requested number of bytes, or all remaining bytes if
            ``num`` is negative.
        """
        self.reader = reader

    cdef void skip(self, int typ) except *:
        if typ == ttype.BOOL:
            self.reader.skip(1)
        elif typ == ttype.BYTE:
            self.reader.skip(1)
        elif typ == ttype.DOUBLE:
            self.reader.skip(8)
        elif typ == ttype.I16:
            self.reader.skip(2)
        elif typ == ttype.I32:
            self.reader.skip(4)
        elif typ == ttype.I64:
            self.reader.skip(8)
        elif typ == ttype.BINARY:
            self.skip_binary()
        elif typ == ttype.STRUCT:
            self.skip_struct()
        elif typ == ttype.MAP:
            self.skip_map()
        elif typ == ttype.SET:
            self.skip_set()
        elif typ == ttype.LIST:
            self.skip_list()

    cdef void skip_struct(self) except *:
        header = self.read_field_begin()
        while header.type != -1:
            self.skip(header.type)
            header = self.read_field_begin()

    cdef void skip_map(self) except *:
        # TODO: This could be optimized to precompute the expected
        # size for fixed width types
        cdef MapHeader header = self.read_map_begin()
        for _ in range(header.size):
            self.skip(header.ktype)
            self.skip(header.vtype)

    cdef void skip_list(self) except *:
        # TODO: This could be optimized to precompute the expected
        # size for fixed width types
        cdef ListHeader header = self.read_list_begin()
        for _ in range(header.size):
            self.skip(header.type)

    cdef void skip_set(self) except *:
        # TODO: This could be optimized to precompute the expected
        # size for fixed width types
        cdef SetHeader header = self.read_set_begin()
        for _ in range(header.size):
            self.skip(header.type)

    cdef void _read(self, char* data, int count) except *:
        self.reader.read(data, count)

    cdef int8_t _byte(self) except *:
        cdef char c
        self._read(&c, 1)
        return <int8_t>c

    cdef int16_t _i16(self) except *:
        cdef char data[2]
        self._read(data, 2)
        return be16toh((<int16_t*>data)[0])

    cdef int32_t _i32(self) except *:
        cdef char data[4]
        self._read(data, 4)
        return be32toh((<int32_t*>data)[0])

    cdef int64_t _i64(self) except *:
        cdef char data[8]
        self._read(data, 8)
        return be64toh((<int64_t*>data)[0])

    cdef double _double(self) except *:
        cdef int64_t value = self._i64()
        return (<double*>(&value))[0]

    cdef bint read_bool(self) except *:
        """Reads a boolean."""
        return self._byte() == 1

    cdef int8_t read_byte(self) except *:
        """Reads a byte."""
        return self._byte()

    cdef double read_double(self) except *:
        """Reads a double."""
        return self._double()

    cdef int16_t read_i16(self) except *:
        """Reads a 16-bit integer."""
        return self._i16()

    cdef int32_t read_i32(self) except *:
        """Reads a 32-bit integer."""
        return self._i32()

    cdef int64_t read_i64(self) except *:
        """Reads a 64-bit integer."""
        return self._i64()

    cdef bytes read_binary(self):
        """Reads a binary blob."""
        cdef int32_t length = self._i32()
        return self.reader.take(length)

    cdef void skip_binary(self) except *:
        cdef int32_t length = self._i32()
        self.reader.skip(length)

    cdef FieldHeader read_field_begin(self) except *:
        cdef int8_t field_type = self._byte()
        if field_type == STRUCT_END:
            return STRUCT_END_HEADER

        cdef int16_t field_id = self._i16()

        return FieldHeader(field_type, field_id)

    cdef MapHeader read_map_begin(self) except *:
        cdef int8_t key_ttype = self._byte()
        cdef int8_t value_ttype = self._byte()
        cdef int32_t length = self._i32()

        return MapHeader(key_ttype, value_ttype, length)

    cdef SetHeader read_set_begin(self) except *:
        cdef int8_t value_ttype = self._byte()
        cdef int32_t length = self._i32()

        return SetHeader(value_ttype, length)

    cdef ListHeader read_list_begin(self) except *:
        cdef int8_t value_ttype = self._byte()
        cdef int32_t length = self._i32()

        return ListHeader(value_ttype, length)

    cdef MessageHeader read_message_begin(self):
        cdef int8_t typ
        cdef int16_t version
        cdef int32_t size
        cdef int32_t seqid
        cdef bytes name

        size = self._i32()
        # TODO with cython, some of the Python-specific hacks around bit
        # twiddling can be skipped.
        if size < 0:
            # strict version:
            #
            #     versionAndType:4 name~4 seqid:4 payload
            version = (size & VERSION_MASK) >> 16
            if version != VERSION:
                raise ThriftProtocolError(
                    'Unsupported version "%r"' % version
                )
            typ = size & TYPE_MASK
            size = self._i32()
            name = self.reader.take(size)
        else:
            # non-strict version:
            #
            #     name:4 type:1 seqid:4 payload
            name = self.reader.take(size)
            typ = self._byte()

        seqid = self._i32()
        return MessageHeader(name, typ, seqid)


cdef class BinaryProtocolWriter(ProtocolWriter):
    """Serializes values using the Thrift Binary protocol."""

    def __cinit__(BinaryProtocolWriter self, WriteBuffer writer):
        """Initialize the writer.

        :param writer:
            WriteBuffer to which requests will be written.
        """
        self.writer = writer

    cdef void _write(BinaryProtocolWriter self, char* data, int length):
        self.writer.write(data, length)

    cdef void write_bool(self, bint value) except *:  # bool:1
        self.write_byte(value)

    cdef void write_byte(BinaryProtocolWriter self, int8_t value) except *:
        # byte:1
        cdef char c = <char>value
        self._write(&c, 1)

    cdef void write_double(self, double value) except *:  # double:8
        # If confused:
        #
        #   <typ*>(&value)[0]
        #
        # Is just "interpret the in-memory representation of value as typ"
        self.write_i64((<int64_t*>(&value))[0])

    cdef void write_i16(BinaryProtocolWriter self, int16_t value) except *:
        # i16:2
        value = htobe16(value)
        self._write(<char*>(&value), 2)

    cdef void write_i32(BinaryProtocolWriter self, int32_t value) except *:
        # i32:4
        value = htobe32(value)
        self._write(<char*>(&value), 4)

    cdef void write_i64(BinaryProtocolWriter self, int64_t value) except *:
        # i64:8
        value = htobe64(value)
        self._write(<char*>(&value), 8)

    cdef void write_binary(BinaryProtocolWriter self, char* value, int32_t length) except *:
        # len:4 str:len
        self.write_i32(length)
        self._write(value, length)

    cdef void write_field_begin(BinaryProtocolWriter self,
                                FieldHeader header) except *:
        # type:1 id:2
        self.write_byte(header.type)
        self.write_i16(header.id)

    cdef void write_struct_end(BinaryProtocolWriter self) except *:
        self.write_byte(STRUCT_END)

    cdef void write_map_begin(BinaryProtocolWriter self,
                              MapHeader header) except *:
        # key_type:1 value_type:1 count:4
        self.write_byte(header.ktype)
        self.write_byte(header.vtype)
        self.write_i32(header.size)

    cdef void write_set_begin(BinaryProtocolWriter self,
                              SetHeader header) except *:
        # value_type:1 count:4
        self.write_byte(header.type)
        self.write_i32(header.size)

    cdef void write_list_begin(BinaryProtocolWriter self,
                               ListHeader header) except *:
        # value_type:1 count:4
        self.write_byte(header.type)
        self.write_i32(header.size)

    cdef void write_message_begin(BinaryProtocolWriter self,
                                  MessageHeader message) except *:
        self.write_binary(message.name, len(message.name))
        self.write_byte(message.type)
        self.write_i32(message.seqid)


cdef class BinaryProtocol(Protocol):
    """Implements the Thrift binary protocol."""

    cpdef ProtocolReader reader(self, ReadBuffer buff):
        return BinaryProtocolReader(buff)

    cpdef ProtocolWriter writer(self, WriteBuffer buff):
        return BinaryProtocolWriter(buff)

    cpdef Message deserialize_message(self, bytes s):
        cdef ReadBuffer buff = ReadBuffer(s)
        return _OldBinaryProtocolReader(buff).read_message()

    cpdef Value deserialize_value(self, int typ, bytes s):
        cdef ReadBuffer buff = ReadBuffer(s)
        return _OldBinaryProtocolReader(buff).read(typ)


__all__ = ['BinaryProtocol']


cdef class _OldBinaryProtocolReader(object):
    """Old version of BinaryProtocolReader that returned Value representations.

    Deserialization was refactored in 1.4 to avoid this step as an optimization.
    This class exists to provide support for backwards compatibility but will
    be removed in a later version.

    .. deprecated:: 1.4
    """

    def __cinit__(self, ReadBuffer reader):
        """Initialize the reader.
        :param reader:
            File-like object with a ``read(num)`` method which returns
            *exactly* the requested number of bytes, or all remaining bytes if
            ``num`` is negative.
        """
        self.reader = reader

    cdef object _reader(self, int8_t typ):
        if typ == ttype.BOOL:
            return self.read_bool
        elif typ == ttype.BYTE:
            return self.read_byte
        elif typ == ttype.DOUBLE:
            return self.read_double
        elif typ == ttype.I16:
            return self.read_i16
        elif typ == ttype.I32:
            return self.read_i32
        elif typ == ttype.I64:
            return self.read_i64
        elif typ == ttype.BINARY:
            return self.read_binary
        elif typ == ttype.STRUCT:
            return self.read_struct
        elif typ == ttype.MAP:
            return self.read_map
        elif typ == ttype.SET:
            return self.read_set
        elif typ == ttype.LIST:
            return self.read_list
        else:
            raise ThriftProtocolError('Unknown TType "%r"' % typ)

    cpdef object read(self, int8_t typ):
        if typ == ttype.BOOL:
            return self.read_bool()
        elif typ == ttype.BYTE:
            return self.read_byte()
        elif typ == ttype.DOUBLE:
            return self.read_double()
        elif typ == ttype.I16:
            return self.read_i16()
        elif typ == ttype.I32:
            return self.read_i32()
        elif typ == ttype.I64:
            return self.read_i64()
        elif typ == ttype.BINARY:
            return self.read_binary()
        elif typ == ttype.STRUCT:
            return self.read_struct()
        elif typ == ttype.MAP:
            return self.read_map()
        elif typ == ttype.SET:
            return self.read_set()
        elif typ == ttype.LIST:
            return self.read_list()
        else:
            raise ThriftProtocolError('Unknown TType "%r"' % typ)

    cdef void _read(self, char* data, int count) except *:
        self.reader.read(data, count)

    cdef int8_t _byte(self) except *:
        cdef char c
        self._read(&c, 1)
        return <int8_t>c

    cdef int16_t _i16(self) except *:
        cdef char data[2]
        self._read(data, 2)
        return be16toh((<int16_t*>data)[0])

    cdef int32_t _i32(self) except *:
        cdef char data[4]
        self._read(data, 4)
        return be32toh((<int32_t*>data)[0])

    cdef int64_t _i64(self) except *:
        cdef char data[8]
        self._read(data, 8)
        return be64toh((<int64_t*>data)[0])

    cdef double _double(self) except *:
        cdef int64_t value = self._i64()
        return (<double*>(&value))[0]

    cdef Message read_message(self):
        cdef int8_t typ
        cdef int16_t version
        cdef int32_t size
        cdef bytes name

        size = self._i32()
        # TODO with cython, some of the Python-specific hacks around bit
        # twiddling can be skipped.
        if size < 0:
            # strict version:
            #
            #     versionAndType:4 name~4 seqid:4 payload
            version = (size & VERSION_MASK) >> 16
            if version != VERSION:
                raise ThriftProtocolError(
                    'Unsupported version "%r"' % version
                )
            typ = size & TYPE_MASK
            size = self._i32()
            name = self.reader.take(size)
        else:
            # non-strict version:
            #
            #     name:4 type:1 seqid:4 payload
            name = self.reader.take(size)
            typ = self._byte()

        seqid = self._i32()
        body = self.read(ttype.STRUCT)

        return Message(name=name, seqid=seqid, body=body, message_type=typ)

    cdef BoolValue read_bool(self):
        """Reads a boolean."""
        return BoolValue(self._byte() == 1)

    cdef ByteValue read_byte(self):
        """Reads a byte."""
        return ByteValue(self._byte())

    cdef DoubleValue read_double(self):
        """Reads a double."""
        return DoubleValue(self._double())

    cdef I16Value read_i16(self):
        """Reads a 16-bit integer."""
        return I16Value(self._i16())

    cdef I32Value read_i32(self):
        """Reads a 32-bit integer."""
        return I32Value(self._i32())

    cdef I64Value read_i64(self):
        """Reads a 64-bit integer."""
        return I64Value(self._i64())

    cdef BinaryValue read_binary(self):
        """Reads a binary blob."""
        cdef int32_t length = self._i32()
        return BinaryValue(self.reader.take(length))

    cdef StructValue read_struct(self):
        """Reads an arbitrary Thrift struct."""
        fields = []

        cdef int8_t field_type = self._byte()
        cdef int16_t field_id

        while field_type != STRUCT_END:
            field_id = self._i16()
            field_value = self.read(field_type)
            fields.append(
                FieldValue(
                    id=field_id,
                    ttype=field_type,
                    value=field_value,
                )
            )

            field_type = self._byte()
        return StructValue(fields)

    cdef MapValue read_map(self):
        """Reads a map."""
        cdef int8_t key_ttype = self._byte()
        cdef int8_t value_ttype = self._byte()
        cdef int32_t length = self._i32()

        kreader = self._reader(key_ttype)
        vreader = self._reader(value_ttype)

        pairs = []
        for i in range(length):
            k = kreader(self)
            v = vreader(self)
            pairs.append(MapItem(k, v))

        return MapValue(
            key_ttype=key_ttype,
            value_ttype=value_ttype,
            pairs=pairs,
        )

    cdef SetValue read_set(self):
        """Reads a set."""
        cdef int8_t value_ttype = self._byte()
        cdef int32_t length = self._i32()

        vreader = self._reader(value_ttype)

        values = []

        for i in range(length):
            values.append(vreader(self))

        return SetValue(
            value_ttype=value_ttype,
            values=values
        )

    cdef ListValue read_list(self):
        """Reads a list."""
        cdef int8_t value_ttype = self._byte()
        cdef int32_t length = self._i32()

        vreader = self._reader(value_ttype)

        values = []

        for i in range(length):
            values.append(vreader(self))

        return ListValue(
            value_ttype=value_ttype,
            values=values
        )
