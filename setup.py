"""
Flask-AutoIndex
---------------

Flask-AutoIndex generates an index page for your `Flask`_ application
automatically. The result just like `mod_autoindex`_, but the look is more
awesome! Look at this:

.. _Flask: http://flask.pocoo.org/
.. _mod_autoindex: http://httpd.apache.org/docs/current/mod/mod_autoindex.html

Links
`````

* `documentation <http://packages.python.org/Flask-AutoIndex/>`_
* `development version
  <http://github.com/sublee/flask-autoindex/zipball/master#egg=flask-autoindex-dev>`_

"""
import re
from setuptools import setup


def run_tests():
    from tests import suite
    return suite()


setup(
    name='Flask-AutoIndex',
    version='0.6',
    license='BSD',
    author='Heungsub Lee',
    author_email=re.sub('((sub).)(.*)', r'\2@\1.\3', 'sublee'),
    url='http://pythonhosted.org/Flask-AutoIndex',
    description='The mod_autoindex for Flask',
    long_description=__doc__,
    packages=['flask_autoindex'],
    include_package_data=True,
    package_data={'flask_autoindex': ['static/*',
                                      'templates/__autoindex__/*']},
    zip_safe=False,
    platforms='any',
    install_requires=['Flask>=0.8', 'Flask-Silk>=0.2', 'future>=0.13.0'],
    test_suite='__main__.run_tests',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    entry_points={
        'console_scripts': [
            'fai = flask_autoindex.run:app.run',
        ],
    },
)
