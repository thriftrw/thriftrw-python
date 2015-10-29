from __future__ import absolute_import

from thrift.transport.THttpClient import THttpClient
from thrift.protocol.TBinaryProtocol import TBinaryProtocolAccelerated

from ping import Ping


trans = THttpClient('http://localhost:8888/thrift')
proto = TBinaryProtocolAccelerated(trans)
client = Ping.Client(proto)

print client.ping('world')
