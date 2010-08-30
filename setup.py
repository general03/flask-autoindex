"""
Flask-AutoIndex
~~~~~~~~~~~~~~~

Generates index page like mod_autoindex.
"""
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(name="Flask-AutoIndex",
      version="0.1.0",
      url="http://github.com/sublee/flask-autoindex",
      license="BSD",
      author="Lee Heung-sub",
      author_email="heung@sublee.kr",
      description="Generates index page like mod_autoindex.",
      long_description=__doc__,
      packages=["flaskext",
                "flaskext.autoindex"],
      package_data={"flaskext.autoindex": ["static/icons/*",
                                           "static/style.css",
                                           "templates/*"]},
      namespace_packages=["flaskext"],
      zip_safe=False,
      platforms="any",
      install_requires=["Flask"],
      test_suite="tests",
      classifiers=[
          "Environment :: Web Environment",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: BSD License",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
          "Topic :: Software Development :: Libraries :: Python Modules"
      ]
)

