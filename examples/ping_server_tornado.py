from __future__ import absolute_import, unicode_literals, print_function

import time
import os.path

from tornado import web
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer

import thriftrw

ping = thriftrw.load(
    os.path.join(os.path.dirname(__file__), 'ping.thrift'),
)


class ThriftRequestHandler(web.RequestHandler):

    def post(self):
        assert self.request.body

        message = ping.loads.message(ping.Ping, self.request.body)
        method, handler = self._METHODS[message.name]

        args = message.body
        resp = method.response(success=handler(self, args))

        reply = ping.dumps.message(resp, seqid=message.seqid)
        self.write(reply)

    def handle_ping(self, args):
        print('Hello, %s' % args.name)
        return ping.Pong(time.time())

    _METHODS = {'ping': (ping.Ping.ping, handle_ping)}


if __name__ == "__main__":
    app = web.Application([
        (r'/thrift', ThriftRequestHandler),
    ])
    HTTPServer(app).listen(8888)
    print('Listening on http://127.0.0.1:8888/thrift')
    IOLoop.current().start()
