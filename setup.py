# coding=utf-8

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='openprovider.py',
    version='0.0.1',
    author='Antagonist B.V.',
    author_email='info@antagonist.nl',
    packages=['openprovider'],
    url='http://pypi.python.org/pypi/openprovider.py/',
    license='LICENSE.rst',
    description='An unofficial library for the OpenProvider API',
    long_description=open('README.rst').read(),
    install_requires=[
        "requests >= 2.3.0",
        "lxml >= 3.3.5",
    ],
    setup_requires=['nose>=1.0']
)