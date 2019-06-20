# Copyright (c) 2019 Uber Technologies, Inc.
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

import pytest
import six


@pytest.mark.parametrize('name, src, kwargs', [
    (
        'Foo', '''
            struct Foo {
                1: required string a
            }
        ''',
        {'a': 'zzz'}
    ),
    (
        'Bar', '''
            union Bar{
                1: binary b
                2: string s
            }
        ''',
        {'s': 'bar'},
    ),
    (
        'Baz', '''
            enum Enum { A = 1, B = 2 }
            struct Baz {
                1: optional Enum e
            }
        ''',
        {'e': 1},
    ),
])
def test_hashable(loads, name, src, kwargs):
    module = loads(src)
    klass = getattr(module, name)
    obj1 = klass(**kwargs)
    obj2 = klass(**kwargs)
    assert hash(obj1) == hash(obj2)
    assert hash(obj1) == hash(obj1)


@pytest.mark.parametrize('name, src, kwargs1, kwargs2', [
    (
        'Foo', '''
            struct Foo {
                1: required string a
            }
        ''',
        {'a': 'zzz'},
        {'a': 'aaa'},
    ),
    (
        'Bar', '''
            union Bar{
                1: binary b
                2: string s
            }
        ''',
        {'s': 'bar'},
        {'b': '0b111'},
    ),
    (
        'Baz', '''
            enum Enum { A = 1, B = 2 }
            struct Baz {
                1: optional Enum e
            }
        ''',
        {'e': 1},
        {'e': 2},
    ),
])
def test_hash_inequality(loads, name, src, kwargs1, kwargs2):
    module = loads(src)
    klass = getattr(module, name)
    obj1 = klass(**kwargs1)
    obj2 = klass(**kwargs2)
    assert hash(obj1) != hash(obj2)


@pytest.mark.skipif(six.PY2, reason="All Python 2 classes are hashable")
@pytest.mark.parametrize('name, src, kwargs', [
    (
        'Foo', '''
            struct Foo {
                1: required string a
                2: required list<string> b
                3: required map<string, string> c = {}
            }
        ''',
        {'a': 'zzz', 'b': ['bar']},
    ),
    (
        'Bar', '''
            union Bar {
                1: binary b
                2: string s
                3: list<string> ls
            }
        ''',
        {'s': 'bar'},
    ),
])
def test_nonhashable(loads, name, src, kwargs):
    module = loads(src)
    klass = getattr(module, name)
    obj = klass(**kwargs)
    with pytest.raises(TypeError):
        hash(obj)
