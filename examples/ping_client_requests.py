from __future__ import absolute_import, unicode_literals, print_function

import os.path
import requests

import thriftrw

ping = thriftrw.load(
    os.path.join(os.path.dirname(__file__), 'ping.thrift'),
)


def main():
    req = ping.Ping.ping.request('world')

    response = requests.post(
        'http://127.0.0.1:8888/thrift',
        data=ping.dumps.message(req, seqid=42),
    )
    reply = ping.loads.message(ping.Ping, response.content)
    assert reply.name == 'ping'
    assert reply.seqid == 42

    resp = reply.body
    print(resp)

if __name__ == "__main__":
    main()
