import os.path
import re
from datetime import datetime


Default = None


class Entry(object):
    """This class wraps file or folder. It is an abstract class, but it returns
    derived class. You can make an instance such as::

        folder = Entry("/home/someone/public_html")
        assert isinstance(foler, Folder)
        file = Entry("/home/someone/public_html/favicon.ico")
        assert isinstance(file, File)
    """

    ICONS_DIRNAME = "icons"
    HIDDEN = re.compile("^\.")

    def __new__(cls, path, root=None):
        """Returns a file or folder instance."""
        abspath = os.path.join(root, path)
        if cls is not Entry:
            return object.__new__(cls)
        elif os.path.isdir(abspath):
            return Folder(path, root)
        elif os.path.isfile(abspath):
            return File(path, root)
        else:
            raise IOError("'{0}' does not exists.".format(fullpath))

    def __init__(self, path, root=None):
        """Initializes an entry instance."""
        self.path = path
        if root:
            self.root = root
        else:
            self.root = os.path.abspath(os.path.curdir)
        self.abspath = os.path.join(self.root, self.path)
        self.name = os.path.basename(self.abspath)
        self.hidden = bool(self.HIDDEN.match(self.name))

    @property
    def modified(self):
        """Returns modified time of this."""
        return datetime.fromtimestamp(os.path.getmtime(self.abspath))

    @classmethod
    def add_icon_rule(cls, icon, rule):
        cls.icon_map.append((icon, rule))

    def guess_icon(self):
        try:
            for icon, rule in self.icon_map:
                if rule(self):
                    return os.path.join(self.ICONS_DIRNAME, icon)
        except AttributeError:
            pass
        try:
            return os.path.join(self.ICONS_DIRNAME, self.default_icon)
        except AttributeError:
            raise GuessError("There is no matched icon.")

    @classmethod
    def browse(cls, path, root=None, sort_by="name", show_hidden=False):
        def compare(ent1, ent2):
            if type(ent1) is not type(ent2):
                return 1 if type(ent1) is File else -1
            else:
                try:
                    return cmp(getattr(ent1, sort_by), getattr(ent2, sort_by))
                except AttributeError:
                    return -1
        abspath = os.path.join(root, path)
        if not os.path.samefile(abspath, root):
            yield ParentFolder(path, root=root)
        entries = os.listdir(abspath)
        entries = (cls(os.path.join(path, name), root=root) for name in entries)
        entries = sorted(entries, cmp=compare)
        for ent in entries:
            if show_hidden or not ent.hidden:
                yield ent


class File(Entry):

    EXTENSION = re.compile("\.(.+)$")

    default_icon = "page_white.png"
    icon_map = []

    def __init__(self, path, root=None):
        super(File, self).__init__(path, root)
        self.size = os.path.getsize(self.abspath)
        try:
            self.ext = re.search(self.EXTENSION, self.name).group(1)
        except AttributeError:
            self.ext = None


class Folder(Entry):

    default_icon = "folder.png"
    icon_map = []


class ParentFolder(Folder):

    default_icon = "arrow_left.png"
    icon_map = []

    def __init__(self, path, root=None):
        super(ParentFolder, self).__init__(os.path.join(path, ".."), root)


class GuessError(RuntimeError): pass

