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

"""
Tests in this file just make sure that the names for functions and types are
valid for use in ``type()`` calls and assignable to ``__name__``.
"""

from __future__ import absolute_import, print_function
# We intentionally don't add unicode_literals here because we want the system
# to use whatever the default is for that version of Python.

import pytest


@pytest.fixture
def service(loads):
    return loads('''
        struct Item {}

        service Service { void someMethod() }
    ''')


def test_function_spec_name(service):
    func_spec = service.Service.someMethod.spec

    def some_func():
        pass

    some_func.__name__ = func_spec.name


def test_type_spec_name(service):
    type_spec = service.Item.type_spec
    type(type_spec.name, (), {})
