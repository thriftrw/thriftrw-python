This project is no longer active. See https://github.com/thriftrw/thriftrw-python/issues/164.

``thriftrw``
============

|test| |coverage| |docs|

``thriftrw`` is a Python library to serialize and deserialize Thrift types.

`Documentation <http://thriftrw.readthedocs.org/en/latest/>`_ is available on
Read The Docs.

.. |test| image:: https://github.com/thriftrw/thriftrw-python/actions/workflows/python.yml/badge.svg
   :target: https://github.com/thriftrw/thriftrw-python/actions/workflows/python.yml

.. |coverage| image:: https://coveralls.io/repos/thriftrw/thriftrw-python/badge.svg?branch=master&service=github
    :target: https://coveralls.io/github/thriftrw/thriftrw-python?branch=master


.. |docs| image:: https://readthedocs.org/projects/thriftrw/badge/?version=latest
    :target: https://readthedocs.org/projects/thriftrw/?badge=latest

Features
--------

* No code generation. The ``.thrift`` files are parsed and compiled in-memory
  at runtime.
* No assumptions about how bytes are sent or received. The library
  concerns itself with serialization and deserialization only.
* Forward and cyclic references in types.

Example
-------

Given the ``.thrift`` file,::

    // blog.thrift

    typedef string PostUUID

    typedef binary RichText

    union Body {
        1: string plainText
        2: RichText richText
    }

    struct PostDetails {
        1: required string author
        2: required string subject
        3: required Body body
    }

    exception UnauthorizedRequestError {
    }

    service BlogService {
        PostUUID newPost(1: PostDetails post)
            throws (1: UnauthorizedRequestError unauthorized);
    }


You can use the library to send and receive requests and responses like so,

.. code-block:: python

    # client.py

    import thriftrw

    blog = thriftrw.load('blog.thrift')
    BlogService = blog.BlogService

    def new_post():
        post = blog.PostDetails(
            author='...',
            subject='...',
            body=blog.Body(plainText='Hello, world!')
        )

        request = BlogService.newPost.request(post)
        payload = blog.dumps(request)

        # send_to_server is implemented by the user.
        response_payload = send_to_server(payload)
        response = blog.loads(BlogService.newPost.response, response_payload)
        if response.unauthorized is not None:
            raise response.unauthorized
        else:
            return response.success


.. code-block:: python

    # server.py

    import thriftrw

    blog = thriftrw.load('blog.thrift')
    BlogService = blog.BlogService

    # The user's server handler calls handle_new_post with the payload.
    def handle_new_post(request_payload):
        request = blog.loads(BlogService.newPost.request, request_payload)
        if request.post.author != 'admin':
            response = BlogService.newPost.response(
                unauthorized=blog.UnauthorizedRequestError()
            )
        else:
            # create_post is implemented by the user.
            post_uuid = create_post(request.post)
            response = BlogService.newPost.response(success=post_uuid)

        return blog.dumps(response)

Message Envelopes
~~~~~~~~~~~~~~~~~

Note that this example sends and receives just the request/response payload. It
does not wrap the payload in a message envelope as expected by Apache Thrift.
If you want to send or receive standard Apache Thrift requests to talk to other
Apache Thrift services, you have to use the ``loads.message`` and
``dumps.message`` APIs. For example,

.. code-block:: python

    # client.py

    def new_post():
        post = blog.PostDetails(...)
        request = BlogService.newPost.request(post)
        payload = blog.dumps.message(request)
        # ^ Instead of using blog.dumps, we use blog.dumps.message to indicate
        # that we want the request wrapped in a message envelope.


        response_payload = send_to_server(payload)

        # Similarly, instead of using blog.loads, we use blog.loads.message to
        # indicate that we want to parse a response stored inside a message.
        response_message = blog.loads.message(BlogService, response_payload)
        response = response_message.body

        if response.unauthorized is not None:
            raise response.unauthorized
        else:
            return response.success


.. code-block:: python

    # server.py

    def handle_request(request_payload):
        message = blog.loads.message(BlogService, request_payload)
        if message.name == 'newPost':
            request = message.body
            # ...
            response = BlogService.newPost.response(success=post_uuid)
            return blog.dumps.message(response, seqid=message.seqid)
            # As before, we use blog.dumps.message instead of blog.dumps.
            # It is important that the server use the same seqid in the
            # response as what was used in the request, otherwise the client
            # will not be able to process out-of-order responses.
        else:
            raise Exception('Unknown method %s' % message.name)

For more information, see `Overview
<http://thriftrw.readthedocs.org/en/latest/overview.html>`_.

Caveats
-------

* Only the Thrift Binary protocol is supported at this time.

Related
-------

* `thriftrw-node <https://github.com/thriftrw/thriftrw-node>`_
* `thriftrw-go <https://github.com/thriftrw/thriftrw-go>`_

License
-------

::

    Copyright (c) 2015 Uber Technologies, Inc.

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:
    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.
    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.
