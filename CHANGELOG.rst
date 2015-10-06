Releases
========

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
