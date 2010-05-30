from setuptools import setup, find_packages

from simpleapi import get_version

setup(
    name='simpleapi',
    version=get_version(),
    description='A simple API-framework to provide an easy to use, consistent and portable client/server-architecture (for django and flask).',
    long_description=open('README.rst').read(),
    author='Florian Schlachter',
    author_email='flori@n-schlachter.de',
    url='http://github.com/flosch/simpleapi/tree/',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python'
    ],
    zip_safe=False,
    test_suite='tests',
)
