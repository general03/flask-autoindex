import os.path
import unittest
from flask import *
from flaskext.autoindex import AutoIndex


browse_root = os.path.abspath(os.path.dirname(__file__))


class ApplicationTestCase(unittest.TestCase):

    def setUp(self):
        app = Flask(__name__)
        AutoIndex(app, browse_root)
        self.app = app

    def get(self, path):
        return self.app.test_client().get(path)

    def test_css(self):
        rv = self.get("/static/style.css")
        assert 200 == rv.status_code, "could not found preloaded css file."

    def test_icon(self):
        rv = self.get("/static/icons/page_white.png")
        assert 294 == len(rv.data), "could not found preloaded icon file."

    def test_browse(self):
        rv = self.get("/")
        assert "Index of /" in rv.data
        assert "__init__.py" in rv.data


class SubdomainTestCase(unittest.TestCase):

    def setUp(self):
        from subdomaintestmodule import mod
        app = Flask(__name__)
        app.config["SERVER_NAME"] = "example.org"
        AutoIndex(mod, browse_root)
        app.register_module(mod)
        self.app = app

    def get(self, path):
        return self.app.test_client().get(path, "http://test.example.org/")

    def test_css(self):
        rv = self.get("/static/style.css")
        assert 200 == rv.status_code, "could not found preloaded css file."

    def test_icon(self):
        rv = self.get("/static/icons/page_white.png")
        assert 294 == len(rv.data), "could not found preloaded icon file."

    def test_browse(self):
        rv = self.get("/")
        assert "Index of /" in rv.data
        assert "__init__.py" in rv.data

    def test_own_static_file(self):
        rv = self.get("/static/helloworld.txt")
        assert "Hello, world!" == rv.data.strip()


class WithoutSubdomainTestCase(unittest.TestCase):

    def setUp(self):
        from testmodule import mod
        app = Flask(__name__)
        AutoIndex(mod, browse_root)
        app.register_module(mod)
        self.app = app

    def get(self, path):
        return self.app.test_client().get(path)

    """
    def test_css(self):
        rv = self.get("/static/style.css")
        assert 200 == rv.status_code, "could not found preloaded css file."

    def test_icon(self):
        rv = self.get("/static/icons/page_white.png")
        assert 294 == len(rv.data), "could not found preloaded icon file."

    def test_browse(self):
        rv = self.get("/")
        assert "Index of /" in rv.data
        assert "__init__.py" in rv.data
    """


if __name__ == "__main__":
    unittest.main()

