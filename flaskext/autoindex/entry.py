# -*- coding: utf-8 -*-
import os.path
import re
from urlparse import urljoin
from datetime import datetime
from mimetypes import guess_type
from fnmatch import fnmatch
from werkzeug import cached_property
from flask import url_for, send_file


Default = None


def _make_mimetype_matcher(mimetype):
    return lambda ent: fnmatch(guess_type(ent.name)[0] or "", mimetype)


def _make_args_for_entry(args, kwargs):
    if not args:
        raise TypeError("path is required, but not given")
    root = autoindex = None
    args = list(args)
    try:
        path = kwargs.get("path", args.pop(0))
        root = kwargs.get("root", args.pop(0))
        autoindex = kwargs.get("autoindex", args.pop(0))
    except IndexError:
        pass
    return (path, root, autoindex)


class Entry(object):
    """This class wraps file or folder. It is an abstract class, but it returns
    a derived instance. You can make an instance such as::

        folder = Entry("/home/someone/public_html")
        assert isinstance(foler, Folder)
        file = Entry("/home/someone/public_html/favicon.ico")
        assert isinstance(file, File)
    """

    HIDDEN = re.compile("^\.")

    def __new__(cls, *args, **kwargs):
        """Returns a file or folder instance."""
        path, root, autoindex = _make_args_for_entry(args, kwargs)
        if root:
            abspath = os.path.join(root.abspath, path)
        else:
            abspath = os.path.abspath(path)
        if os.path.isdir(abspath):
            return Folder.__new__(Folder, path, root, autoindex)
        elif os.path.isfile(abspath):
            return object.__new__(File)
        else:
            raise IOError("'{0}' does not exists.".format(abspath))

    def __init__(self, path, root=None, autoindex=None):
        """Initializes an entry instance."""
        self.root = root
        self.autoindex = autoindex
        try:
            rootpath = self.root.abspath
            if not self.autoindex and self.root:
                self.autoindex = self.root.autoindex
        except AttributeError:
            rootpath = ""
        self.path = path
        self.abspath = os.path.join(rootpath, self.path)
        self.name = os.path.basename(self.abspath)
        self.hidden = bool(self.HIDDEN.match(self.name))

    def is_root(self):
        """Returns ``True`` if it is a root folder."""
        return isinstance(self, RootFolder) or \
               os.path.samefile(self.abspath, self.root.abspath)

    @property
    def parent(self):
        if self.is_root():
            return None
        elif os.path.samefile(os.path.dirname(self.abspath),
                              self.root.abspath):
            return self.root
        return Entry(os.path.dirname(self.path), self.root)

    @property
    def modified(self):
        """Returns modified time of this."""
        return datetime.fromtimestamp(os.path.getmtime(self.abspath))

    @classmethod
    def add_icon_rule(cls, icon, rule=None):
        """Adds a new icon rule globally."""
        cls.icon_map.append((icon, rule))

    @classmethod
    def add_icon_rule_by_name(cls, icon, name):
        """Adds a new icon rule by the name globally."""
        cls.add_icon_rule(icon, lambda ent: ent.name == name)

    @classmethod
    def add_icon_rule_by_class(cls, icon, _class):
        """Adds a new icon rule by the class globally."""
        cls.add_icon_rule(icon, lambda ent: isinstance(ent, _class))

    def guess_icon(self):
        """Guesses an icon from itself."""
        def get_icon_url():
            try:
                if self.autoindex:
                    icon_map = self.autoindex.icon_map + self.icon_map
                else:
                    icon_map = self.icon_map
                for icon, rule in icon_map:
                    if not rule and callable(icon):
                        matched = icon = icon(self)
                    else:
                        matched = rule(self)
                    if matched:
                        return icon
            except AttributeError:
                pass
            try:
                return self.default_icon
            except AttributeError:
                raise GuessError("There is no matched icon.")
        return urljoin(url_for("silkicon", filename=""), get_icon_url())


class File(Entry):
    """This class wraps a file."""

    EXTENSION = re.compile("\.(.+)$")

    default_icon = "page_white.png"
    icon_map = []
    converter_map = []

    def __init__(self, path, root=None, autoindex=None):
        super(File, self).__init__(path, root, autoindex)
        try:
            self.ext = re.search(self.EXTENSION, self.name).group(1)
        except AttributeError:
            self.ext = None

    def to_html(self):
        """Converts to HTML format."""
        text = self.data.decode("utf-8")
        try:
            if self.autoindex:
                converter_map = self.autoindex.converter_map + \
                                self.converter_map
            else:
                converter_map = self.converter_map
            for converter, rule in converter_map:
                if rule(self):
                    return converter(self)
        except AttributeError:
            pass
        raise MarkupError("It could not be converted to HTML.")

    @cached_property
    def data(self):
        """Data of this file."""
        return "".join(open(self.abspath).readlines())

    @cached_property
    def mimetype(self):
        """A mimetype of this file."""
        return guess_type(self.abspath)

    @cached_property
    def size(self):
        """A size of this file."""
        return os.path.getsize(self.abspath)

    @classmethod
    def add_icon_rule_by_ext(cls, icon, ext):
        """Adds a new icon rule by the file extension globally."""
        cls.add_icon_rule(icon, lambda ent: ent.ext == ext)

    @classmethod
    def add_icon_rule_by_mimetype(cls, icon, mimetype):
        """Adds a new icon rule by the mimetype globally."""
        cls.add_icon_rule(icon, _make_mimetype_matcher(mimetype))

    @classmethod
    def add_html_converter(cls, converter, rule):
        """Adds a new html converter globally."""
        cls.converter_map.append((converter, rule))

    @classmethod
    def add_html_converter_by_ext(cls, converter, ext):
        """Adds a new html converter by the file extension globally."""
        cls.add_html_converter(converter, lambda ent: ent.ext == ext)

    @classmethod
    def add_html_converter_by_mimetype(cls, converter, mimetype):
        """Adds a new html converter by the mimetype globally."""
        cls.add_html_converter(converter, _make_mimetype_matcher(mimetype))


class Folder(Entry):
    """This class wraps a folder."""

    default_icon = "folder.png"
    icon_map = []

    def __new__(cls, *args, **kwargs):
        path, root, autoindex = _make_args_for_entry(args, kwargs)
        if not root:
            return RootFolder.__new__(RootFolder, path, autoindex)
        return object.__new__(cls)

    def __init__(self, path, root=None, autoindex=None):
        super(Folder, self).__init__(path, root, autoindex)

    def browse(self, sort_by="name", order=1, show_hidden=False):
        """It is a generator. Each item is an child entry."""
        def compare(ent1, ent2):
            def asc():
                if sort_by != "modified" and type(ent1) is not type(ent2):
                    return 1 if type(ent1) is File else -1
                else:
                    try:
                        return cmp(getattr(ent1, sort_by),
                                   getattr(ent2, sort_by))
                    except AttributeError:
                        return cmp(getattr(ent1, "name"),
                                   getattr(ent2, "name"))
            return asc() * order
        if not self.is_root():
            yield _ParentFolder(self)
        entries = os.listdir(self.abspath)
        entries = (Entry(os.path.join(self.path, name), self.root) \
                   for name in entries)
        entries = sorted(entries, cmp=compare)
        for ent in entries:
            if show_hidden or not ent.hidden:
                yield ent

    def get_readme(self, readme_filename="README",
                   compare=lambda x, y: -cmp(len(x), len(y))):
        """Returns a readme file. If this folder has many readme files, it
        sorts them and returns the first readme file.
        
        :param readme_filename: a name of readme file. The default is
                                ``README``.
        :param compare: a function for sort readme files. when it is passed,
                        this method returns a file which has a longest name.
        """
        readmes = sorted((p for p in os.listdir(self.abspath) \
                          if p == readme_filename or \
                             p.startswith(readme_filename + ".")), cmp=compare)
        if readmes:
            return self.get_file(readmes[0])
        raise IOError("{0} folder has no readme file".format(self.name))

    def get_file(self, filename):
        """Returns the child file as a :class:`File`."""
        if filename in self:
            return File(os.path.join(self.path, filename), self.root)
        else:
            raise IOError("{0} does not exist".format(filename))

    def __contains__(self, path):
        return os.path.exists(os.path.join(self.abspath, path))


class RootFolder(Folder):
    """This class wraps a root folder."""

    default_icon = "server.png"
    icon_map = []

    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    def __init__(self, path, autoindex=None):
        super(RootFolder, self).__init__(".", autoindex=autoindex)
        self.abspath = os.path.abspath(path)


class _ParentFolder(Folder):

    default_icon = "arrow_turn_up.png"
    icon_map = []

    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    def __init__(self, child_folder):
        path = os.path.join(child_folder.path, "..")
        super(_ParentFolder, self).__init__(path, child_folder.root)


class GuessError(RuntimeError): pass
class MarkupError(RuntimeError): pass

