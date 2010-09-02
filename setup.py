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

* `documentation <http://docs.sublee.kr/flask-autoindex>`_
* `development version
  <http://github.com/sublee/flask-autoindex/zipball/master>`_

"""
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def run_tests():
    from tests import suite
    return suite()


setup(
    name="Flask-AutoIndex",
    version="0.2.0",
    url="http://github.com/sublee/flask-autoindex",
    license="BSD",
    author="Lee Heung-sub",
    author_email="heung@sublee.kr",
    description="A mod_autoindex for Flask",
    long_description=__doc__,
    packages=["flaskext", "flaskext.autoindex"],
    include_package_data=True,
    package_data={"flaskext.autoindex": ["static/*", "templates/*"]},
    namespace_packages=["flaskext"],
    zip_safe=False,
    platforms="any",
    install_requires=[
        "Flask>=0.6",
        "Flask-Silk"
    ],
    test_suite="__main__.run_tests",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
)

