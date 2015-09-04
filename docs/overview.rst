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
    :raises thriftrw.protocol.ThriftProtocolError:
        If ``payload`` was an invalid Thrift Binary Protocol payload.
    :raises TypeError, ValueError:
        If the payload was a vaild Thrift Binary Protocol payload but did not
        contain the object that was requested or if the required fields for it
        were missing.

.. py:attribute:: services

    Collection of all classes generated for all services defined in the source
    thrift file.

.. py:attribute:: types

    Collection of all classes generated for all types defined in the source
    thrift file.

.. py:attribute:: constants

    Mapping of constant name to value for all constants defined in the source
    thrift file.

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

Differences from Apache Thrift
------------------------------

``thriftrw`` interprets Thrift files slightly differently from Apache Thrift.
Here are the differences:

-  For ``struct`` and ``exception`` types, every field **MUST** specify whether
   it is ``required`` or ``optional``.

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
