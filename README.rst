``thriftrw`` is a Python library to serialize and deserialize Thrift types at
runtime. It does not concern itself with client/server logic or exception
handling.

It supports only the Thrift Binary protocol at this time.

For example, given::

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

You can use the library to send and receive requests and responses

.. code-block:: python

    import thriftrw

    blog = thriftrw.load('blog.thrift')
    BlogService = blog.BlogService

    # client-side:

    def new_post():
        post = blog.PostDetails(
            author='...',
            subject='...',
            body=blog.Body(plain_text='Hello, world!')
        )

        request = BlogService.new_post.request(post)
        payload = request.dump()

        response_payload = send_to_server(payload)

        response = BlogService.new_post.response.load(
            response_payload
        )
        if response.unauthorized is not None:
            raise response.unauthorized
        else:
            return response.success

    # server-side:

    def handle_new_post(request_payload):
        request = BlogService.new_post.request.load(request_payload)

        if request.post.author != 'admin':
            response = BlogService.new_post.response(
                unauthorized=blog.UnauthorizedRequestError()
            )
        else:
            post_uuid = create_post(request.post)
            response = BlogService.new_post.response(success=post_uuid)

        response_payload = response.dump()
        return response_payload

Note that attribute and method names are converted from ``camelCase`` to
``snake_case`` on the Python side.
