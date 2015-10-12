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

from .struct import StructTypeSpec


__all__ = ['ExceptionTypeSpec']


class ExceptionTypeSpec(StructTypeSpec):
    """Spec for ``exception`` types defined in the Thrift file.

    This is exactly the same as :py:class:`thriftrw.spec.StructTypeSpec`
    except that the generated class inherits the ``Exception`` class.
    """

    def __init__(self, *args, **kwargs):
        kwargs['base_cls'] = Exception
        super(ExceptionTypeSpec, self).__init__(*args, **kwargs)

    def __str__(self):
        return 'ExceptionTypeSpec(name=%r, cls=%r, fields=%r)' % (
            self.name, self.cls, self.fields
        )

    __repr__ = __str__
