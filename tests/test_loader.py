# Copyright (c) 2016 Uber Technologies, Inc.
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

from textwrap import dedent

import pytest

from thriftrw.errors import ThriftCompilerError
from thriftrw.loader import Loader


def test_load_from_file(tmpdir):
    tmpdir.join('my_service.thrift').write('''
        struct Foo {
            1: required string a
            2: optional string b
        }
    ''')

    my_service = Loader().load(str(tmpdir.join('my_service.thrift')))
    my_service.Foo(b='b', a='a')


def test_load_from_file_missing_requiredness(tmpdir):
    tmpdir.join('my_service.thrift').write('''
        struct Foo {
            1: required string a
            2: string b
        }
    ''')

    with pytest.raises(ThriftCompilerError) as exc_info:
        Loader().load(str(tmpdir.join('my_service.thrift')))

    assert (
        '"b" of "Foo" on line 4 does not explicitly specify requiredness.'
        in str(exc_info)
    )


def test_load_from_file_non_strict_missing_requiredness(tmpdir):
    tmpdir.join('my_service.thrift').write('''
        struct Foo {
            1: required string a
            2: string b
        }

        exception Bar {
            1: string message
        }
    ''')

    loader = Loader(strict=False)
    m = loader.load(str(tmpdir.join('my_service.thrift')))
    m.Foo(b='b', a='a')

    m.Bar(message='foo')
    m.Bar()


def test_caching(tmpdir, monkeypatch):
    tmpdir.join('my_service.thrift').write('''
        struct Foo {
            1: required string a
            2: optional string b
        }
    ''')

    path = str(tmpdir.join('my_service.thrift'))
    loader = Loader()

    mod1 = loader.load(path)
    mod2 = loader.load(path)
    assert mod1 is mod2


@pytest.mark.unimport('foo.bar.svc')
def test_install_absolute(tmpdir, monkeypatch):
    module_root = tmpdir.mkdir('foo')
    module_root.join('__init__.py').ensure()

    thrift_file = module_root.join('service.thrift')
    thrift_file.write(
        'struct Foo { 1: required string a; 2: optional string b }'
    )

    py_file = module_root.join('bar.py')
    py_file.write(
        dedent('''
            import thriftrw

            thriftrw.install(%r, name='svc')
        ''' % str(thrift_file))
    )

    monkeypatch.syspath_prepend(str(tmpdir))

    from foo.bar.svc import Foo

    assert Foo(a='bar') == Foo(a='bar')


@pytest.mark.unimport('foo.service', 'foo.bar')
def test_install_relative(tmpdir, monkeypatch):
    module_root = tmpdir.mkdir('foo')
    module_root.join('service.thrift').write('struct Bar {}')

    module_root.join('bar.py').write(dedent('''
        from __future__ import absolute_import
        from .service import Bar
    '''))

    module_root.join('__init__.py').write(dedent('''
        import thriftrw

        thriftrw.install('service.thrift')
    '''))

    monkeypatch.syspath_prepend(str(tmpdir))

    from foo.bar import Bar

    assert Bar() == Bar()


@pytest.mark.unimport('foo.service')
def test_install_twice(tmpdir, monkeypatch):
    module_root = tmpdir.mkdir('foo')
    module_root.join('__init__.py').write(dedent('''
        import thriftrw

        def go():
            return thriftrw.install('service.thrift')
    '''))

    module_root.join('service.thrift').write(
        'struct Foo { 1: required string a 2: optional string b }'
    )

    monkeypatch.syspath_prepend(str(tmpdir))

    from foo import go

    with pytest.raises(ImportError):
        from foo.service import Foo
        Foo()

    assert go() is go()

    from foo.service import Foo
    assert go().Foo is Foo
