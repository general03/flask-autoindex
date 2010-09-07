# -*- coding: utf-8 -*-
from .entry import File, Folder, Default


class Converters(object):

    def add_markdown_converter(self):
        """Adds a markdown converter if :mod:`markdown` exists."""
        try:
            from markdown import Markdown
            def markdown_converter(file):
                text = file.data.decode("utf-8")
                return Markdown().convert(text)
            for ext in ["markdown", "md"]:
                File.add_html_converter_by_ext(markdown_converter, ext)
        except ImportError:
            pass

    def add_html_converter(self):
        """Adds a HTML converter."""
        skip = lambda f: f.data.encode("utf-8")
        for ext in ["html", "htm", "xhtml"]:
            File.add_html_converter_by_ext(skip, ext)

    def add_plain_converter(self):
        """Adds a plain text converter."""
        def plain_converter(file):
            text = file.data.decode("utf-8")
            return "<pre>{0}</pre>".format(text)
        def is_plain(file):
            return file.ext == "txt" or not file.ext
        File.add_html_converter(plain_converter, is_plain)


converters = Converters()
for meth in dir(converters):
    if meth.startswith("add_") and meth.endswith("_converter"):
        getattr(converters, meth)()

