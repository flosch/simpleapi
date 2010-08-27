from setuptools import setup, find_packages

setup(
    name='simpleapi',
    version='0.0.9',
    description='A simple API-framework to provide an easy to use, consistent and portable client/server-architecture (for django, flask and a lot more).',
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
    install_requires=open("requirements.txt", "r").read().split()
)
