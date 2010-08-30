import os.path
import unittest
from flask import *
from flaskext.autoindex import AutoIndex


class SubdomainTestCase(unittest.TestCase):

    def setUp(self):
        app = Flask(__name__)
        app.config["SERVER_NAME"] = "example.org"
        from subdomaintestmodule import mod
        app.register_module(mod)
        self.app = app
        self.mod = mod

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


if __name__ == "__main__":
    unittest.main()

