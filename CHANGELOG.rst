Releases
========

1.3.1 (unreleased)
------------------

- Optimized serialization and deserialization performance by removing an
  unnecessary intermediate layer.
- Optimized validation at object construction time by skipping the parsing
  of nested structs and unions since they would have been validated already
  anyway.
- Due to build incompatibility issues, pypy3 support is temporarily being
  dropped. The library is unlikely to break, but no guarantees exist.


1.3.0 (2016-09-13)
------------------

- Changed ``PrimitiveTypeSpec.validate()`` to check that the values of
  integer fields fit in the required number of bits.
- Include the field ID and struct name in the exception messages from
  ``StructTypeSpec.validate()``.


1.2.5 (2016-09-07)
------------------

- Fixed a bug that caused mutations to default values of structs to be
  persisted across calls.
- Fixed a bug where the ``strict`` flag was not respected for exceptions.


1.2.4 (2016-03-04)
------------------

- Fixed a bug that caused optional arguments to show up out of order in
  ``struct`` docstrings.


1.2.3 (2016-02-16)
------------------

- Fixed bug where ``Decimal`` and ``Fraction`` values were disallowed for
  ``float`` fields.


1.2.2 (2016-02-15)
------------------

- Re-add the changes from 1.2.0 with a fix. Serialization and deserialization
  should be fast again.


1.2.1 (2016-02-11)
------------------

- Revert changes made in 1.2.0 because they unintentionally break some
  str/unicode concerns in TypeSpecs.


1.2.0 (2016-02-11)
------------------

- Serialization and deserialization to and from binary is now almost twice as
  fast.


1.1.0 (2016-01-11)
------------------

- Expose ``result_type`` on the args type for service functions.
- Expose ``service`` on function spec.
- Expose the contents of the Thrift file on compiled modules under the
  ``__thrift_source__`` attribute.
- Expose a reference back to the module on generated types as
  ``__thrift_module__``.
- Don't fail compilation if fields in unions specify themselves as
  ``optional``.
- Added ``i8`` as an alias for ``byte`` in Thrift files.
- Allow multiple enum items to have the same value.
- Fixed a bug where the line number of constant lists and maps was incorrect in
  the AST.


1.0.1 (2015-12-11)
------------------

- Fixed bug where type annotations without values weren't supported by the
  grammar.


1.0.0 (2015-11-06)
------------------

- ``include`` statements are now supported. For more information, see
  :ref:`including-modules`.
- Added support for message envelopes. This makes it possible to talk with
  standard Apache Thrift services and clients. For more information, see
  :ref:`calling-apache-thrift`.
- Constant and default values may now be structs or unions, represented in the
  Thrift file as maps with string keys.
- Significant performance improvements to the ``BinaryProtocol``
  implementation.
- Removed ``thriftrw.wire.TType`` in favor of the ``thriftrw.wire.ttype``
  module.
- ``MapValue`` now contains ``MapItem`` objects instead of key-value tuple
  pairs.
- Request and response ``TypeSpecs`` now have a reference back to the
  ``FunctionSpec``.
- ``ServiceSpec`` now provides a ``lookup`` method to look up ``FunctionSpecs``
  by name.
- Removed the ``force`` option on ``Loader.load``.
- In generated modules, renamed the ``types``, ``constants`` and ``services``
  attributes to ``__types__``, ``__constants__``, and ``__services__``.


0.5.2 (2015-10-19)
------------------

- Fixed a bug which prevented default values for enums from being plain
  integers.


0.5.1 (2015-10-16)
------------------

- Fix a bug in the parser that prevented starting identifier names with
  ``true`` or ``false``.
- Allow passing 0 and 1 as default values for ``bool``. These will
  automatically be cast to boolean.


0.5.0 (2015-10-14)
------------------

- Core modules have been cythonized for additional performance improvements.
- **Breaking** All custom exceptions are exported by the ``thriftrw.errors``
  module only. This includes ``ThriftProtocolError`` and ``EndOfInputError``.
- ``UnknownExceptionError`` is now raised if an unrecognized exception is
  encountered while parsing service method responses.


0.4.2 (2015-10-13)
------------------

- Lists and sets now allow arbitrary iterables as input.
- Lists may be used to provide default values for sets.


0.4.1 (2015-10-12)
------------------

- Now uses ``io.BytesIO`` for speed improvements in Python 2.
- Fixed a bug which allowed empty responses for non-void methods.
- Fixed a bug which caused the ``eq`` methods for structs, unions, and
  exceptions to raise ``AttributeError`` if the value being compared was of the
  wrong type.


0.4.0 (2015-10-09)
------------------

- Added an option to disable "required/optional" strictness on structs.
- Added ``to_primitive`` and ``from_primitive`` methods to generated types to
  allow converting struct, union, and exception values to and from primitive
  representations.
- Added a ``validate`` method to all ``TypeSpecs``.
- Changed to perform validation during struct, union, or exception construction
  instead of performing it during serialization.
- Allow unicode to be passed for ``binary`` types.


0.3.3 (2015-10-05)
------------------

- Default values for binary fields are no longer unicode.


0.3.2 (2015-09-15)
------------------

- Backwards compatibility for Python 2.7.6 and earlier due to Python #19099.


0.3.1 (2015-09-09)
------------------

- Allow binary values to be passed for ``string`` types.


0.3.0 (2015-09-09)
------------------

- Support ``oneway`` functions.


0.2.0 (2015-09-08)
------------------

- Export a mapping of constants in the generated module under the ``constants``
  attribute.
- Added ``thriftrw.install`` to install a Thrift file as a submodule of a
  module.
- Expose ``thriftrw.spec.FunctionResultSpec`` with information on the return
  and exception types of the function.


0.1.0 (2015-08-28)
------------------

- Initial release.
