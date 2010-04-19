from setuptools import setup, find_packages

setup(
	name='simpleapi',
	version='0.0.1',
	description='A simple API-framework for django to provide an easy to use, consistent and portable client/server-architecture.',
	long_description=open('README.rst').read(),
	author='Florian Schlachter',
	author_email='flori@n-schlachter.de',
	url='http://github.com/flosch/simpleapi',
	packages=find_packages(),
	classifiers=[
		'Development Status :: 3 - Alpha',
		'Environment :: Web Environment',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: MIT License',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Framework :: Django',
	],
	zip_safe=False,
)
