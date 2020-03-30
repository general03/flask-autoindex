"""
Flask-AutoIndex
---------------

Flask-AutoIndex generates an index page for your `Flask`_ application
automatically. The result is similar to the one produced by the Apache
module `mod_autoindex`_, but the look is more awesome!

.. _Flask: https://palletsprojects.com/p/flask/
.. _mod_autoindex: http://httpd.apache.org/docs/current/mod/mod_autoindex.html

Links
`````

* `Documentation <https://flask-autoindex.readthedocs.io/>`_
* `Code repository and issue tracker <https://github.com/general03/flask-autoindex>`_

"""
import re

from setuptools import setup


def run_tests():
    from tests import suite
    return suite()


setup(
    name='Flask-AutoIndex',
    version='0.6.6',
    license='MIT',
    author='RIGAUDIE David',
    url='https://flask-autoindex.readthedocs.io',
    description='The mod_autoindex for Flask',
    long_description=__doc__,
    packages=['flask_autoindex'],
    include_package_data=True,
    package_data={'flask_autoindex': ['static/*',
                                      'templates/__autoindex__/*']},
    zip_safe=False,
    platforms='any',
    install_requires=['Flask>=1.1', 'Flask-Silk>=0.2', 'future>=0.13.0'],
    test_suite='__main__.run_tests',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    entry_points={
        'console_scripts': [
            'fai = flask_autoindex.run:app.run',
        ],
    },
)
