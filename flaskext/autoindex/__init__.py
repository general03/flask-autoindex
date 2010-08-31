import os.path
from flask import *
from werkzeug import cached_property
from jinja2 import FileSystemLoader
from .entry import *
from . import icons


__dir__ = os.path.abspath(os.path.dirname(__file__))
__name__ = "__autoindex__"


class AutoIndex(object):
    """This class makes the Flask application or module to serve automacally
    generated index page. The wrapped site(application or module) will route
    ``/`` and ``/<path:path>``.

    You can make your application to serve generated index::

        app = Flask(__name__)
        idx = AutoIndex(app, "/home/someone/public_html")
        assert isinstance(idx, AutoIndexApplication)

    Or with module::

        mod = Module(__name__, subdomain="mod")
        idx = AutoIndex(mod, "/home/otherone/public_html")
        assert isinstance(idx, AutoIndexModule)
    """

    icon_map = []

    def _register_shared_autoindex(self, state=None, app=None):
        """Registers a magic module named __autoindex__."""
        app = app or state.app
        if __name__ not in app.modules:
            app.modules[__name__] = self.base

    def __new__(cls, base, browse_root=None):
        """Checks a base."""
        if cls is not AutoIndex:
            return object.__new__(cls)
        elif isinstance(base, Flask):
            return AutoIndexApplication(base, browse_root)
        elif isinstance(base, Module):
            return AutoIndexModule(base, browse_root)
        else:
            raise TypeError("'base' should be Flask or Module.")

    def __init__(self, base, browse_root=None):
        """Initializes an autoindex instance. And overrides ``jinja_loader``
        of the wrapped application or module to :meth:`AutoIndex.jinja_loader`.
        """
        self.base, self.browse_root = base, browse_root
        self.base.jinja_loader = self.jinja_loader
        for rule in "/", "/<path:path>":
            self.browse = self.base.route(rule)(self.browse)

    def browse(self, path="."):
        """Browses the files from the path."""
        abspath = os.path.join(self.browse_root, path)
        if os.path.isdir(abspath):
            sort_by = request.args.get("sort_by", "name")
            entries = Entry.browse(path, autoindex=self,
                                   root=self.browse_root, sort_by=sort_by)
            titlepath = "/" + ("" if path == "." else path)
            prefix = self.template_prefix
            options = dict(path=titlepath, entries=entries, sort_by=sort_by)
            return render_template("{0}browse.html".format(prefix), **options)
        elif os.path.isfile(abspath):
            return send_file(abspath)
        else:
            return abort(404)

    def add_icon_rule(self, icon, rule=None, ext=None, mimetype=None,
                      name=None, filename=None, foldername=None):
        if name:
            filename = name
            foldername = name
        if ext:
            File.add_icon_rule_by_ext.im_func(self, icon, ext)
        if mimetype:
            File.add_icon_rule_by_mimetype.im_func(self, icon, mimetype)
        if filename:
            File.add_icon_rule_by_name.im_func(self, icon, filename)
        if foldername:
            Folder.add_icon_rule_by_name.im_func(self, icon, foldername)
        if callable(rule):
            Entry.add_icon_rule.im_func(self, icon, rule)

    @property
    def template_prefix(self):
        raise NotImplementedError()

    def send_static_file(self, filename):
        """Serves a static file. It finds the file from autoindex internal
        static directory first. If it failed to find the file, it finds from
        the wrapped application or module's static directory.
        """
        global_static = os.path.join(__dir__, "static")
        if os.path.isfile(os.path.join(global_static, filename)):
            static = global_static
        else:
            static = os.path.join(self.base.root_path, "static")
        return send_from_directory(static, filename)

    @cached_property
    def jinja_loader(self):
        """The jinja loader with merged template paths."""
        paths = [os.path.join(path, "templates") \
                 for path in __dir__, self.base.root_path]
        return FileSystemLoader(paths)


class AutoIndexApplication(AutoIndex):

    template_prefix = ""

    def __init__(self, app, browse_root=None):
        super(AutoIndexApplication, self).__init__(app, browse_root)
        self.app = app
        self.app.view_functions["static"] = self.send_static_file
        self._register_shared_autoindex(app=self.app)


class AutoIndexModule(AutoIndex):

    def __init__(self, mod, browse_root=None):
        super(AutoIndexModule, self).__init__(mod, browse_root)
        self.mod = self.base
        self.mod._record(self._register_shared_autoindex)
        self.mod.send_static_file = self.send_static_file

    @cached_property
    def template_prefix(self):
        return self.mod.name + "/"

