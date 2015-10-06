import os
import sys
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
PY2 = sys.version_info[0] == 2

with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()

with open(os.path.join(here, 'CHANGELOG.rst')) as f:
    CHANGELOG = f.read()


REQUIREMENTS = [
    'waitress==0.8.10',
    'cliquet[monitoring]>=2.8,<2.9',
    'hkdf==0.0.3',
    'PyNaCl==0.3.0',
    'syncclient==0.5.0',
]

if PY2:
    REQUIREMENTS += [
        "pyopenssl==0.15.1",
        "ndg-httpsclient==0.4.0",
        "pyasn1==0.1.9"
    ]

ENTRY_POINTS = {
    'paste.app_factory': [
        'main = syncto:main',
    ]}

setup(name='syncto',
      version='1.0.0',
      description='Read Firefox Sync server using Kinto API.',
      long_description=README + "\n\n" + CHANGELOG,
      license='Apache License (2.0)',
      classifiers=[
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: Implementation :: CPython",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
          "License :: OSI Approved :: Apache Software License"
      ],
      keywords="web services",
      author='Mozilla Services',
      author_email='services-dev@mozilla.com',
      url='https://syncto.readthedocs.org/',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=REQUIREMENTS,
      entry_points=ENTRY_POINTS)
