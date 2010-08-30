import os.path
import re
from datetime import datetime


Default = None


class Entry(object):

    ICONS_DIRNAME = "icons"
    HIDDEN = re.compile("^\.")

    def __new__(cls, path, root=None):
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
        return datetime.fromtimestamp(os.path.getmtime(self.abspath))

    def guess_icon(self):
        raise NotImplementedError("'guess_icon' should be overridden.")

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
            yield Folder(os.path.join(path, ".."), root=root)
        entries = os.listdir(abspath)
        entries = (cls(os.path.join(path, name), root=root) for name in entries)
        entries = sorted(entries, cmp=compare)
        for ent in entries:
            if show_hidden or not ent.hidden:
                yield ent


class File(Entry):

    EXTENSION = re.compile("\.(.+)$")
    ICONS_BY_EXT = {Default: "page_white.png",
                    "py": "page_white_python.png",
                    "pyc": "python.png"}

    def __init__(self, path, root=None):
        super(File, self).__init__(path, root)
        self.size = os.path.getsize(self.abspath)
        try:
            self.ext = re.search(self.EXTENSION, self.name).group(1)
        except AttributeError:
            self.ext = None

    def guess_icon(self):
        try:
            icon = self.ICONS_BY_EXT[self.ext]
        except KeyError:
            icon = self.ICONS_BY_EXT[Default]
        return os.path.join(self.ICONS_DIRNAME, icon)


class Folder(Entry):

    ICONS_BY_NAME = {Default: "folder.png",
                     "..": "arrow_left.png"}

    def guess_icon(self):
        try:
            icon = self.ICONS_BY_NAME[self.name]
        except KeyError:
            icon = self.ICONS_BY_NAME[Default]
        return os.path.join(self.ICONS_DIRNAME, icon)

