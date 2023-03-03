#!/usr/bin/env python

import os
import re

from setuptools import setup
from setuptools import find_packages
from setuptools.command.sdist import sdist as _sdist
from setuptools.extension import Extension as _Extension

cmdclass = {}
ext_modules = []

cython_modules = [
    'thriftrw._buffer',
    'thriftrw._cython',
    'thriftrw._runtime',
    'thriftrw.protocol.core',
    'thriftrw.protocol.binary',
    'thriftrw.spec.base',
    'thriftrw.spec.check',
    'thriftrw.spec.common',
    'thriftrw.spec.enum',
    'thriftrw.spec.exc',
    'thriftrw.spec.field',
    'thriftrw.spec.list',
    'thriftrw.spec.map',
    'thriftrw.spec.reference',
    'thriftrw.spec.primitive',
    'thriftrw.spec.service',
    'thriftrw.spec.set',
    'thriftrw.spec.spec_mapper',
    'thriftrw.spec.struct',
    'thriftrw.spec.typedef',
    'thriftrw.spec.union',
    'thriftrw.wire.message',
    'thriftrw.wire.mtype',
    'thriftrw.wire.ttype',
    'thriftrw.wire.value',
]

extension_extras = {}

# If Cython is available we will re-cythonize the pyx files, otherwise we just
# compile the packaged C files.
extension_filetype = '.c'

Extension = None
try:
    import Cython.Distutils

    cmdclass.update(build_ext=Cython.Distutils.build_ext)

    # Check if we forgot to add something to cython_modules.
    for root, _, files in os.walk('thriftrw'):
        for name in files:
            if not name.endswith('.pyx'):
                continue
            path = os.path.join(root, name)
            module = path.replace('/', '.')[:-4]
            if module not in cython_modules:
                raise Exception(
                    'Module "%s" (%s) is not present in the '
                    '"cython_modules" list.'
                    % (module, path)
                )

    Extension = Cython.Distutils.Extension
    extension_filetype = '.pyx'

    cython_directives = {
        'embedsignature': True,
    }

    if os.getenv('THRIFTRW_PROFILE'):
        # Add hooks for the profiler in the generated C code.
        cython_directives['profile'] = True

    if os.getenv('THRIFTRW_COVERAGE'):
        # Add line tracing hooks to the generated C code. The hooks aren't
        # actually enabled unless the CYTHON_TRACE macre is also set. This
        # affects performance negatively and should only be used during
        # testing.
        extension_extras['define_macros'] = [('CYTHON_TRACE', '1')]
        cython_directives['linetrace'] = True

    if cython_directives:
        extension_extras['cython_directives'] = cython_directives
except ImportError:
    pass

if Extension is None:
    Extension = _Extension


for module in cython_modules:
    ext_modules.append(
        Extension(
            module,
            [module.replace('.', '/') + extension_filetype],
            **extension_extras
        )
    )


class sdist(_sdist):
    """This forces us to always re-compile extensions before releasing."""

    def run(self):
        try:
            from Cython.Build import cythonize

            cythonize([
                module.replace('.', '/') + '.pyx' for module in cython_modules
            ])
        except ImportError:
            pass
        _sdist.run(self)


cmdclass['sdist'] = sdist


version = None
with open('thriftrw/__init__.py', 'r') as f:
    for line in f:
        m = re.match(r'^__version__\s*=\s*(["\'])([^"\']+)\1', line)
        if m:
            version = m.group(2)
            break

if not version:
    raise Exception(
        'Could not determine version number from thriftrw/__init__.py'
    )


with open('README.rst') as f:
    long_description = f.read()

setup(
    name='thriftrw',
    version=version,
    description=(
        'A library to serialize and deserialize Thrift values.'
    ),
    long_description=long_description,
    author='Abhinav Gupta',
    author_email='abg@uber.com',
    url='https://github.com/thriftrw/thriftrw-python',
    packages=find_packages(exclude=('tests', 'tests.*')),
    license='MIT',
    install_requires=['ply'],
    tests_require=['pytest', 'mock'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    ext_modules=ext_modules,
    cmdclass=cmdclass,
)
