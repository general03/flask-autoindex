from past.builtins import cmp
from future import standard_library
standard_library.install_hooks()
# -*- coding: utf-8 -*-
from datetime import datetime
from fnmatch import fnmatch
from mimetypes import guess_type
import functools
import os
import re
from future.utils import with_metaclass
from future.moves.urllib.parse import urljoin
from flask import url_for, send_file
from werkzeug import cached_property


Default = None


is_same_path = lambda x, y: os.stat(x) == os.stat(y)


def _make_mimetype_matcher(mimetype):
    return lambda ent: fnmatch(guess_type(ent.name)[0] or '', mimetype)


def _make_args_for_entry(args, kwargs):
    if not args:
        raise TypeError('path is required, but not given')
    rootdir = autoindex = None
    args = list(args)
    try:
        path = kwargs.get('path', args.pop(0))
        rootdir = kwargs.get('rootdir', args.pop(0))
        autoindex = kwargs.get('autoindex', args.pop(0))
    except IndexError:
        pass
    return (path, rootdir, autoindex)


class _EntryMeta(type):
    """The meta class for :class:`Entry`."""

    def __call__(cls, *args, **kwargs):
        """If an instance already initialized, just returns."""
        ent = cls.__new__(cls, *args, **kwargs)
        try:
            ent.path
        except AttributeError:
            ent.__init__(*args, **kwargs)
        return ent


class Entry(with_metaclass(_EntryMeta, object)):
    """This class wraps file or directory. It is an abstract class, but it
    returns a derived instance. You can make an instance such as::

        directory = Entry('/home/someone/public_html')
        assert isinstance(foler, Directory)
        file = Entry('/home/someone/public_html/favicon.ico')
        assert isinstance(file, File)
    """

    HIDDEN = re.compile('^\.')

    def __new__(cls, *args, **kwargs):
        """Returns a file or directory instance."""
        path, rootdir, autoindex = _make_args_for_entry(args, kwargs)
        if rootdir:
            abspath = os.path.join(rootdir.abspath, path)
        else:
            abspath = os.path.abspath(path)
        if os.path.isdir(abspath):
            return Directory.__new__(Directory, path, rootdir, autoindex)
        elif os.path.isfile(abspath):
            return File.__new__(File, path, rootdir, autoindex)
        else:
            raise IOError('{0} does not exists.'.format(abspath))

    def __init__(self, path, rootdir=None, autoindex=None):
        """Initializes an entry instance."""
        self.rootdir = rootdir
        self.autoindex = autoindex
        try:
            rootpath = self.rootdir.abspath
            if not autoindex and self.rootdir:
                self.autoindex = self.rootdir.autoindex
        except AttributeError:
            rootpath = ''
        self.path = path
        self.abspath = os.path.join(rootpath, self.path)
        self.name = os.path.basename(self.abspath)
        self.hidden = bool(self.HIDDEN.match(self.name))
        if self.rootdir:
            self.rootdir._register_descendant(self)

    def is_root(self):
        """Returns ``True`` if it is a root directory."""
        return isinstance(self, RootDirectory)

    @property
    def parent(self):
        if self.is_root():
            return None
        elif is_same_path(os.path.dirname(self.abspath), self.rootdir.abspath):
            return self.rootdir
        return Entry(os.path.dirname(self.path), self.rootdir)

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
                raise GuessError('There is no matched icon.')
        try:
            return urljoin(url_for('.silkicon', filename=''), get_icon_url())
        except (AttributeError, RuntimeError):
            return 'ERROR'
            return get_icon_url()


class File(Entry):
    """This class wraps a file."""

    EXTENSION = re.compile('\.([^.]+)$')

    default_icon = 'page_white.png'
    icon_map = []

    def __new__(cls, path, rootdir=None, autoindex=None):
        try:
            return rootdir._descendants[(path, autoindex)]
        except (AttributeError, KeyError):
            pass
        return object.__new__(cls)

    def __init__(self, path, rootdir=None, autoindex=None):
        super(File, self).__init__(path, rootdir, autoindex)
        try:
            self.ext = re.search(self.EXTENSION, self.name).group(1)
        except AttributeError:
            self.ext = None

    @cached_property
    def data(self):
        """Data of this file."""
        with open(self.abspath) as f:
            return ''.join(f.readlines())

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


class Directory(Entry):
    """This class wraps a directory."""

    default_icon = 'folder.png'
    icon_map = []

    def __new__(cls, *args, **kwargs):
        """If the path is same with root path, it returns a
        :class:`RootDirectory` object.
        """
        path, rootdir, autoindex = _make_args_for_entry(args, kwargs)
        if not rootdir:
            return RootDirectory(path, autoindex)
        try:
            return rootdir._descendants[(path, autoindex)]
        except KeyError:
            pass
        rootpath = rootdir.abspath
        if is_same_path(os.path.join(rootpath, path), rootpath):
            if not rootdir:
                rootdir = RootDirectory(rootpath, autoindex)
            return rootdir
        return object.__new__(cls)

    def explore(self, sort_by='name', order=1, show_hidden=False):
        """It is a generator. Each item is a child entry."""

        def compare(ent1, ent2):
            def asc():
                if sort_by != 'modified' and type(ent1) is not type(ent2):
                    return 1 if type(ent1) is File else -1
                else:
                    try:
                        return cmp(getattr(ent1, sort_by),
                                   getattr(ent2, sort_by))
                    except AttributeError:
                        return cmp(getattr(ent1, 'name'),
                                   getattr(ent2, 'name'))
            return asc() * order
        if not self.is_root():
            yield _ParentDirectory(self)
            rootdir = self.rootdir
        else:
            rootdir = self
        dirlist = os.listdir(self.abspath)
        entries = []
        for name in dirlist:
            try:
                entries.append(Entry(os.path.join(self.path, name), rootdir))
            except IOError:
                continue  # ignore stuff like broken links
        entries = sorted(entries, key=functools.cmp_to_key(compare))
        for ent in entries:
            if show_hidden or not ent.hidden:
                yield ent

    def get_child(self, childname):
        """Returns a child file or directory."""
        if childname in self:
            if self.path != '.':
                path = os.path.join(self.path, childname)
            else:
                path = childname
            return Entry(path, self.rootdir)
        else:
            raise IOError('{0} does not exist'.format(childname))

    def __contains__(self, path_or_entry):
        """Checks this directory has a file or directory.

            public_html = Directory('public_html')
            'favicon.ico' in public_html
            File('favicon.ico', public_html) in public_html
        """
        if isinstance(path_or_entry, Entry):
            path = os.path.relpath(path_or_entry.path, self.path)
            if os.path.pardir in path:
                return False
        else:
            path = path_or_entry
        return os.path.exists(os.path.join(self.abspath, path))


class RootDirectory(Directory):
    """This class wraps a root directory."""

    default_icon = 'server.png'
    icon_map = []
    _rootdirs = {}

    def __new__(cls, path, autoindex=None):
        try:
            return RootDirectory._rootdirs[(path, autoindex)]
        except KeyError:
            return object.__new__(cls)

    def __init__(self, path, autoindex=None):
        super(RootDirectory, self).__init__('.', autoindex=autoindex)
        self.abspath = os.path.abspath(path)
        self.rootdir = self
        self._descendants = {}
        RootDirectory._register_rootdir(self)

    @classmethod
    def _register_rootdir(cls, rootdir):
        cls._rootdirs[(rootdir.abspath, rootdir.autoindex)] = rootdir

    def _register_descendant(self, entry):
        self._descendants[(entry.path, entry.autoindex)] = entry


class _ParentDirectory(Directory):
    """This class wraps a parent directory."""

    default_icon = 'arrow_turn_up.png'
    icon_map = []

    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    def __init__(self, child_directory):
        path = os.path.join(child_directory.path, '..')
        super(_ParentDirectory, self).__init__(path, child_directory.rootdir)


class GuessError(RuntimeError): pass
class MarkupError(RuntimeError): pass
