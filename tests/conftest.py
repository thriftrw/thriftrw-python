# Copyright (c) 2015 Uber Technologies, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import absolute_import, unicode_literals, print_function

import sys


def unimport(*names):
    """Removes imported modules from ``sys.modules``.

    The given modules and all their parents will be removed from
    ``sys.modules``.  For example, if ``unimport('os.path')`` is called, both
    ``os.path`` and ``os`` will be removed from ``sys.modules``.

    The intented use case for this is to tell the system to forget about
    modules created during tests to ensure that other tests that create
    similarly named modules don't conflict with existing modules.

    :param names:
        List of modules to be removed. The given modules and all their parents
        will be removed.
    """
    modules = set()
    for name in names:
        parts = name.split('.')
        while parts:
            modules.add('.'.join(parts))
            parts = parts[:-1]

    for module in modules:
        sys.modules.pop(module, None)


def pytest_runtest_teardown(item, nextitem):
    """Teardown hook for unimport.

    Can be used like so,

    .. code-block:: python

        @pytest.mark.unimport('foo.bar', 'foo.qux')
        def test_something():
            from foo.bar import Bar

            # ...
    """
    marker = item.get_marker('unimport')
    if marker:
        unimport(*marker.args)
