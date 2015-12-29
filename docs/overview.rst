Overview
========

``thriftrw`` is a Python library to serialize and deserialize Thrift types. It
parses ``.thrift`` files and generates types based on the IDL in-memory at
runtime.

To use ``thriftrw``, you simply call :py:func:`thriftrw.load` with the path to
the ``.thrift`` file.

.. code-block:: python

    import thriftrw

    keyvalue = thriftrw.load('keyvalue.thrift')

This generates a module which contains the generated types and constants.

Importing generated modules
---------------------------

When using just :py:func:`thriftrw.load`, you cannot reference the generated
module in ``import`` statements. For example, the following will not work:

.. code-block:: python

    keyvalue = thriftrw.load('keyvalue.thrift')

    from keyvalue import KeyValue  # ImportError

That's because the system doesn't yet know that the module name ``keyvalue``
maps to that generated module. This can be remedied by using
:py:func:`thriftrw.install`.

.. code-block:: python

    # some_module.py

    import thriftrw

    keyvalue = thriftrw.install('keyvalue.thrift')

This will install ``keyvalue`` as a submodule of ``some_module`` so that you
can do,

.. code-block:: python

    from some_module.keyvalue import KeyValue

For more information, see :py:func:`thriftrw.install`.

What gets generated?
--------------------

The generated module contains two top-level functions ``dumps`` and ``loads``.

.. py:function:: dumps(obj)

    Serializes the given object using the Thrift Binary Protocol.

    .. code-block:: python

        request = keyvalue.KeyValue.getItem.request('somekey')
        request_payload = keyvalue.dumps(request)

    :param obj:
        Object to be serialized
    :returns bytes:
        The object's serialized representation
    :raises TypeError:
        If the type of a value specified for a field doesn't match what was
        specified in the IDL.
    :raises ValueError:
        If the type matches but the value is not a valid candidate for a
        specific field.

.. py:function:: loads(cls, payload)

    Deserializes an object of type ``cls`` from ``payload`` using the Thrift
    Binary Protocol.

    .. code-block:: python

        request = keyvalue.loads(
            keyvalue.KeyValue.getItem.request,
            request_payload,
        )

    :param cls:
        Type of object being deserialized.
    :param bytes payload:
        Bytes containing the serialized representation of a ``cls`` object
    :raises thriftrw.errors.ThriftProtocolError:
        If ``payload`` was an invalid Thrift Binary Protocol payload.
    :raises TypeError, ValueError:
        If the payload was a vaild Thrift Binary Protocol payload but did not
        contain the object that was requested or if the required fields for it
        were missing.

.. py:function:: dumps.message(obj, seqid=0)

    Serializes the given request or response and puts it inside a message
    envelope.

    .. code-block:: python

        request = keyvalue.KeyValue.getItem.request('somekey')
        payload = keyvalue.dumps.message(request, seqid)

    The message type is determined automatically based on whether ``obj`` is a
    request or a response, and whether it is for a function that is ``oneway``
    or not.

    For more information, see :ref:`calling-apache-thrift`.

    :param obj:
        A request or response object. This is obtained by using the ``request``
        or ``response`` attributes on a
        :py:class:`thriftrw.spec.ServiceFunction`.
    :param seqid:
        If given, this is the sequence ID used for the message envelope.
        Clients can use the ``seqid`` to match out-of-order responses up with
        their requests. Servers **must** use the same ``seqid`` in their
        responses as what they got in the request.
    :returns:
        Serialized payload representing the message.

.. py:function:: loads.message(service, payload)

    Deserializes a message containing a request or response for the given
    service from the payload.

    .. code-block:: python

        message = keyvalue.loads.message(keyvalue.KeyValue, payload)
        print message.name          # => 'getItem'
        print message.message_type  # => 1  (CALL)
        request = message.body

    The service function is resolved based on the name specified in the
    message, and a request or response is returned based on the message type.

    For more information, see :ref:`calling-apache-thrift`.

    :param service:
        Service object representing a specific service.
    :param bytes payload:
        Payload to parse.
    :returns thriftrw.value.Message:
        The parsed Message.
    :raises thriftrw.errors.UnknownExceptionError:
        If the message type was ``EXCEPTION``, an ``UnknownExceptionError`` is
        raised with the parsed exception struct in the body.
    :raises thriftrw.errors.ThriftProtocolError:
        If the method name was not recognized or any other payload parsing
        errors.

.. py:attribute:: __services__

    Collection of all classes generated for all services defined in the source
    thrift file.

    .. versionchanged:: 1.0

        Renamed from ``services`` to ``__services__``.

.. py:attribute:: __types__

    Collection of all classes generated for all types defined in the source
    thrift file.

    .. versionchanged:: 1.0

        Renamed from ``types`` to ``__types__``.

.. py:attribute:: __includes__

    Collection of modules which were referenced via ``include`` statements in
    the generated module.

    .. versionadded:: 1.0

.. py:attribute:: __thrift_source__

    Contents of the .thrift file from which this module was compiled.

    .. versionadded:: 1.1

.. py:attribute:: __constants__

    Mapping of constant name to value for all constants defined in the source
    thrift file.

    .. versionchanged:: 1.0

        Renamed from ``constants`` to ``__constants__``.

Includes
~~~~~~~~

For an include::

    include "./shared.thrift"

The generated module will include a top-level attribute ``shared`` which
references the generated module for ``shared.thrift``.

Note that paths in include statements are relative to the directory containing
the Thrift file and they must be in the from ``./foo.thrift``,
``./foo/bar.thrift``, ``../baz.thrift``, and so on.

Structs
~~~~~~~

Given the struct::

    struct User {
        1: required string name
        2: optional string email
        3: required bool isActive = true
    }

A ``User`` class gets generated with a constructor similar to the following.

.. code-block:: python

    class User(object):

        def __init__(self, name, email=None, isActive=None):
            if name is None:
                raise TypeError(..)
            if isActive is None:
                isActive = True

            # ..

A ``TypeError`` is raised if required arguments are missing.

Note that fields of a struct **MUST** specify in the IDL whether they are
required or optional.

See :py:class:`thriftrw.spec.StructTypeSpec` for more details.

Exceptions
~~~~~~~~~~

Classes generated for exceptions behave exactly the same as ``struct`` classes
except that they inherit the ``Exception`` class.

See :py:class:`thriftrw.spec.ExceptionTypeSpec` for more details.

Unions
~~~~~~

Given the union::

    union Value {
        1: string stringValue
        2: i32 integerValue
    }

A ``Value`` class gets generated with a constructor similar to the following.

.. code-block:: python

    class Value(object):

        def __init__(self, stringValue=None, integerValue=None):
            if stringValue is not None and integerValue is not None:
                raise TypeError(..)
            if stringValue is None and integerValue is None:
                raise TypeError(..)

            # ..

A ``TypeError`` is raised if multiple non-None values are given or if no
non-None values are given.

See :py:class:`thriftrw.spec.UnionTypeSpec` for more details.

Enums
~~~~~

Given the enum::

    enum Status {
        QUEUED,
        RUNNING,
        FAILED,
        SUCCEEDED,
    }

A ``Status`` class similar to the following gets generated,

.. code-block:: python

    class Status(object):

        QUEUED = 0
        RUNNING = 1
        FAILED = 2
        SUCCEEDED = 3

See :py:class:`thriftrw.spec.EnumTypeSpec` for more details.

Services
~~~~~~~~

Given the service::

    service KeyValue {
        void putValue(1: string key, 2: Value value);
        Value getValue(1: string key)
            throws
              (1: ResourceDoesNotExist doesNotExist);
        list<Value> listValues();
    }

A class similar to the following gets generated,

.. code-block:: python

    class KeyValue(object):
        putValue = ServiceFunction(..)
        getValue = ServiceFunction(..)
        listValues = ServiceFunction(..)

Where each declared function gets its own :py:class:`ServiceFunction`. Each
``ServiceFunction`` has a ``request`` and ``response`` attribute which points
to the request or response class for that method. For example, the
``ServiceFunction`` for ``getValue`` can be used like so,

.. code-block:: python

    request = KeyValue.getValue.request('some_key')

    # Return values are provided using the name 'success'.
    successful_response = KeyValue.getValue.response(success=Value(..))

    # Exceptions arre attached using the name of the exception.
    failed_response = KeyValue.getValue.response(
        doesNotExist=ResourceDoesNotExist(..)
    )

For functions that don't return any values, ``response`` may be instantiated
with no arguments.

.. code-block:: python

    successful_response = KeyValue.putValue.response()

See :py:class:`thriftrw.spec.ServiceSpec` for more details.

Constants
~~~~~~~~~

Constants are made available as-is in the generated module::

    const string LAST_UPDATED = "2015-08-28"

.. code-block:: python

    LAST_UPDATED = '2015-08-28'

Constants and default values may be structs or unions if represented as maps
with string keys in the Thrift file::

    struct Item { 1: required string key, 2: required i32 value }

    const Item ZERO_ITEM = {'key': '', 'value': 0}

The generated module will include a ``ZERO_ITEM`` definition equivalent to,

.. code-block:: python

    ZERO_ITEM = Item(key=u'', value=0)


Primitive representations
-------------------------

.. versionadded:: 0.4

It is sometimes required to convert values of generated types into primitive
representations of themselves. This may be required so that we can pass the
value to a serialization library or just to provide a readable reprsentation of
the value. ``thriftrw`` provides the ``to_primitive`` and ``from_primitive``
methods on generated types for ``struct``, ``union``, and ``exception`` types
to do just that.

.. py:method:: to_primitive(self)

    Converts ``self`` into a dictionary mapping field names of the struct,
    union, or exception, to primitive representations of the field values.
    Fields with ``None`` values are skipped.

.. py:classmethod:: from_primitive(cls, value)

    Reads a primitive representation of a value of this class. Unrecognized
    fields are ignored.

For example, given::


    struct User {
        1: required string name
        2: optional string email
        3: required bool isActive = true
    }

We have,

.. code-block:: python

    john = User(name='John Smith', email='john@example.com')
    assert john.to_primitive() == {
        'name': 'John Smith',
        'email': 'john@example.com',
        'isActive': True,
    }

    jane = User(
        name='Jane Smith',
        email='jane@example.com',
        isActive=True,
    )
    assert jane == User.from_primitive({
        'name': 'Jane Smith',
        'email': 'jane@example.com',
    })

Primitive representations of values are composed of ``bool``, ``bytes``,
``float``, ``str`` (``unicode`` in Python < 3), ``int``, ``long``, ``dict``,
and ``list``. The Thrift types map to primitive types like so:

=============   ==============
Thrift Type     Primitive Type
=============   ==============
``bool``        ``bool``
``byte``        ``int``
``i16``         ``int``
``i32``         ``int``
``i64``         ``long``
``double``      ``float``
``string``      ``str`` (``unicode`` in Python < 3)
``binary``      ``bytes``
``list``        ``list``
``map``         ``dict``
``set``         ``list``
``struct``      ``dict``
``union``       ``dict``
``exception``   ``dict``
=============   ==============

.. _including-modules:

Including other Thrift files
----------------------------

Types, services, and constants defined in different Thrift files may be
referenced by using ``include`` statements with paths **relative to the current
.thrift file**. The paths must be in the form ``./foo.thrift``,
``./foo/bar.thrift``, ``../baz.thrift``, and so on.

Included modules will automatically be compiled along with the module that
included them, and they will be made available in the generated module with the
**base name** of the included file (without the extension).

For example, given::

    // shared/types.thrift

    struct UUID {
        1: required i64 high
        2: required i64 low
    }

And::

    // services/user.thrift

    include "../shared/types.thrift"

    struct User {
        1: required types.UUID uuid
    }

You can do the following

.. code-block:: python

    service = thriftrw.load('services/user.thrift')

    user_uuid = service.shared.UUID(...)
    user = service.User(uuid=user_uuid)

    # ...

Also note that you can ``load()`` Thrift files that have already been loaded
without extra cost because the result is cached by the system.

.. code-block:: python

    service = thriftrw.load('services/user.thrift')
    types = thriftrw.load('shared/types.thrift')

    assert service.types is types

.. _calling-apache-thrift:

Calling Apache Thrift
----------------------

The output you get from ``service.dumps(MyService.getFoo.request(..))`` and
``service.dumps(MyService.getFoo.response(..))`` contains just the serialized
request or response. This is not enough to talk with Apache Thrift services.

Standard Apache Thrift payloads wrap the serialized request or response in a
message envelope containing the following additional information:

- The name of the method. This is ``getFoo`` in the example above.
- Whether this message contains a request, oneway request, unexpected failure,
  or response.
- Sequence ID of the message. This lets clients that receive out-of-order
  responses match them up with their corresponding requests.

Use of message envelopes is **required** if you want to communicate with Apache
Thrift services or clients generated by Apache Thrift.

To wrap your a request or response in a message envelope, simply use
``dumps.message`` instead of ``dumps``, and specify a sequence ID.

.. code-block:: python

    request = MyService.getFoo.request(...)
    payload = service.dumps.message(request, seqid=10)

Similarly, to parse responses wrapped inside message envelopes, use
``loads.message`` instead of ``loads``.

.. code-block:: python

    def handle_request(request_payload):
        message = service.loads.message(MyService, request_payload)
        # It is important that we use the same seqid in the response
        # envelope.
        seqid = message.seqid
        request = message.body

        # ...

        response_payload = service.dumps.message(response, seqid=seqid)

On the server side, it's important that the response ``seqid`` be the same as
the request ``seqid``.

Differences from Apache Thrift
------------------------------

``thriftrw`` interprets Thrift files slightly differently from Apache Thrift.
Here are the differences:

-  For ``struct`` and ``exception`` types, every field **MUST** specify whether
   it is ``required`` or ``optional``. This is to ensure that there is no
   ambiguity around how different code generators handle the default.

-  ``thriftrw`` allows forward references to types and constants. That is,
   types and constants may be referenced that are defined further down in the
   file::

       typedef Foo Bar

       struct Foo {
           // ..
       }

-  ``thriftrw`` allows cyclic references between types::

       union Tree {
           1: Leaf leaf
           2: Branch branch
       }

       struct Leaf {
           1: required i32 value
       }

       struct Branch {
           1: required Tree leftTree
           2: required Tree rightTree
       }
