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

from .struct cimport StructTypeSpec
from .union cimport UnionTypeSpec
from .base cimport TypeSpec


cdef class FunctionArgsSpec(StructTypeSpec):
    cdef public FunctionSpec function


cdef class FunctionResultSpec(UnionTypeSpec):
    cdef public TypeSpec return_spec
    cdef public list exception_specs
    cdef public FunctionSpec function
    cdef public object exception_ids


cdef class FunctionSpec(object):
    cdef readonly unicode name
    cdef public FunctionArgsSpec args_spec
    cdef public FunctionResultSpec result_spec
    cdef readonly bint oneway
    cdef public bint linked
    cdef public object surface
    cdef public ServiceSpec service

    cpdef FunctionSpec link(self, scope, ServiceSpec service)


cdef class ServiceSpec(object):
    cdef readonly unicode name
    cdef public list functions
    cdef public object parent
    cdef public dict _functions
    cdef public bint linked
    cdef public object surface

    cpdef ServiceSpec link(self, scope)
