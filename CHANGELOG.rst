Releases
========

0.5.0 (unreleased)
------------------

- Core modules have been cythonized for additional performance improvements.


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
