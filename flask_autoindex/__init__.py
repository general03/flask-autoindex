# -*- coding: utf-8 -*-
"""
    flask_autoindex
    ~~~~~~~~~~~~~~~

    The mod_autoindex for `Flask <http://flask.pocoo.org/>`_.

    :copyright: (c) 2010-2013 by Heungsub Lee.
    :license: BSD, see LICENSE for more details.
"""
from __future__ import absolute_import
from future.builtins import str
from future.builtins import object
import os
import re

from flask import *
from flask.ext.silk import Silk
from jinja2 import FileSystemLoader, TemplateNotFound
from werkzeug import cached_property

from .entry import *
from . import icons


__version__ = '0.5'
__autoindex__ = '__autoindex__'


class AutoIndex(object):
    """This class makes the Flask application to serve automatically
    generated index page. The wrapped application will route ``/`` and
    ``/<path:path>`` when ``add_url_rules`` is ``True``. Here's a simple
    example::

        app = Flask(__name__)
        AutoIndex(app, '/home/someone/public_html', add_url_rules=True)

    :param base: a Flask application.
    :param browse_root: a path which is served by root address. By default,
                        this is the working directory, but you can set it to
                        fix your app to always use one location if you like.
    :param add_url_rules: if it is ``True``, the wrapped application routes
                          ``/`` and ``/<path:path>`` to autoindex. default
                          is ``True``.
    :param template_context: would be passed to the Jinja2 template when
                             rendering an AutoIndex page.
    :param silk_options: keyword options for :class:`flask.ext.silk.Silk`.
    """

    shared = None

    def _register_shared_autoindex(self, state=None, app=None):
        """Registers a magic module named __autoindex__."""
        app = app or state.app
        if __autoindex__ not in app.blueprints:
            static_folder = os.path.join(__path__[0], 'static')
            template_folder = os.path.join(__path__[0], 'templates')
            shared = Blueprint(__autoindex__, __name__,
                               template_folder=template_folder)
            @shared.route('/__autoindex__/<path:filename>')
            def static(filename):
                return send_from_directory(static_folder, filename)
            app.register_blueprint(shared)

    def __new__(cls, base, *args, **kwargs):
        if isinstance(base, Flask):
            return object.__new__(AutoIndexApplication)
        elif isinstance(base, Blueprint):
            return object.__new__(AutoIndexBlueprint)
        else:
            raise TypeError("'base' should be Flask or Blueprint.")

    def __init__(self, base, browse_root=None, add_url_rules=True,
                 template_context=None, silk_options=None,
                 show_hidden=False):
        """Initializes an autoindex instance."""
        self.base = base
        if browse_root:
            browse_root = str(browse_root)
        else:
            browse_root = os.path.curdir
        self.rootdir = RootDirectory(browse_root, autoindex=self)
        self.template_context = template_context
        if silk_options is None:
            silk_options = {}
        silk_options['silk_path'] = silk_options.get('silk_path', '/__icons__')
        self.silk = Silk(self.base, **silk_options)
        self.show_hidden = show_hidden
        self.icon_map = []
        self.converter_map = []
        if add_url_rules:
            @self.base.route('/')
            @self.base.route('/<path:path>')
            def autoindex(path='.'):
                return self.render_autoindex(path)

    def render_autoindex(self, path, browse_root=None, template=None,
                         template_context=None, endpoint='.autoindex',
                         show_hidden=None, sort_by='name',
                         mimetype=None):
        """Renders an autoindex with the given path.

        :param path: the relative path.
        :param browse_root: if it is specified, it used to a path which is
                            served by root address.
        :param template: the template name.
        :param template_context: would be passed to the Jinja2 template when
                                 rendering an AutoIndex page.
        :param endpoint: an endpoint which is a function.
        :param show_hidden: whether to show hidden files (starting with '.')
        :param sort_by: the property to sort the entrys by.
        :param mimetype: set static mime type for files (no auto detection).
        """
        if browse_root:
            rootdir = RootDirectory(browse_root, autoindex=self)
        else:
            rootdir = self.rootdir
        path = re.sub(r'\/*$', '', path)
        abspath = os.path.join(rootdir.abspath, path)
        if os.path.isdir(abspath):
            sort_by = request.args.get('sort_by', sort_by)
            order = {'asc': 1, 'desc': -1}[request.args.get('order', 'asc')]
            curdir = Directory(path, rootdir)
            if show_hidden == None: show_hidden = self.show_hidden
            entries = curdir.explore(sort_by=sort_by, order=order,
                                     show_hidden=show_hidden)
            if callable(endpoint):
                endpoint = endpoint.__name__
            context = {}
            if template_context is not None:
                context.update(template_context)
            if self.template_context is not None:
                context.update(self.template_context)
            context.update(
                curdir=curdir, entries=entries,
                sort_by=sort_by, order=order, endpoint=endpoint)
            if template:
                return render_template(template, **context)
            try:
                template = '{0}autoindex.html'.format(self.template_prefix)
                return render_template(template, **context)
            except TemplateNotFound as e:
                template = '{0}/autoindex.html'.format(__autoindex__)
                return render_template(template, **context)
        elif os.path.isfile(abspath):
            if mimetype:
                return send_file(abspath, mimetype=mimetype)
            else:
                return send_file(abspath)
        else:
            return abort(404)

    def add_icon_rule(self, icon, rule=None, ext=None, mimetype=None,
                      name=None, filename=None, dirname=None, cls=None):
        """Adds a new icon rule.

        There are many shortcuts for rule. You can use one or more shortcuts in
        a rule.

        `rule`
            A function which returns ``True`` or ``False``. It has one argument
            which is an instance of :class:`Entry`. Example usage::

                def has_long_name(ent):
                    return len(ent.name) > 10
                idx.add_icon_rule('brick.png', rule=has_log_name)

            Now the application represents files or directorys such as
            ``very-very-long-name.js`` with ``brick.png`` icon.

        `ext`
            A file extension or file extensions to match with a file::

                idx.add_icon_rule('ruby.png', ext='ruby')
                idx.add_icon_rule('bug.png', ext=['bug', 'insect'])

        `mimetype`
            A mimetype or mimetypes to match with a file::

                idx.add_icon_rule('application.png', mimetype='application/*')
                idx.add_icon_rule('world.png', mimetype=['image/icon', 'x/*'])

        `name`
            A name or names to match with a file or directory::

                idx.add_icon_rule('error.png', name='error')
                idx.add_icon_rule('database.png', name=['mysql', 'sqlite'])

        `filename`
            Same as `name`, but it matches only a file.

        `dirname`
            Same as `name`, but it matches only a directory.

        If ``icon`` is callable, it is used to ``rule`` function and the result
        is used to the url for an icon. This way is useful for getting an icon
        url dynamically. Here's a nice example::

            def get_favicon(ent):
                favicon = 'favicon.ico'
                if type(ent) is Directory and favicon in ent:
                    return '/' + os.path.join(ent.path, favicon)
                return False
            idx.add_icon_rule(get_favicon)

        Now a directory which has a ``favicon.ico`` guesses the ``favicon.ico``
        instead of silk's ``folder.png``.
        """
        if name:
            filename = name
            directoryname = name
        call = lambda m, *args: m.__func__(self, *args)
        if ext:
            call(File.add_icon_rule_by_ext, icon, ext)
        if mimetype:
            call(File.add_icon_rule_by_mimetype, icon, mimetype)
        if filename:
            call(File.add_icon_rule_by_name, icon, filename)
        if dirname:
            call(Directory.add_icon_rule_by_name, icon, dirname)
        if cls:
            call(Entry.add_icon_rule_by_class, icon, cls)
        if callable(rule) or callable(icon):
            call(Entry.add_icon_rule, icon, rule)

    @property
    def template_prefix(self):
        raise NotImplementedError()


class AutoIndexApplication(AutoIndex):
    """An AutoIndex which supports flask applications."""

    template_prefix = ''

    def __init__(self, app, browse_root=None, **silk_options):
        super(AutoIndexApplication, self).__init__(app, browse_root,
                                                   **silk_options)
        self.app = app
        self._register_shared_autoindex(app=self.app)


class AutoIndexBlueprint(AutoIndex):
    """An AutoIndex which supports flask blueprints.

    .. versionadded:: 0.3.1
    """

    def __init__(self, blueprint, browse_root=None, **silk_options):
        super(AutoIndexBlueprint, self).__init__(blueprint, browse_root,
                                                 **silk_options)
        self.blueprint = self.base
        self.blueprint.record_once(self._register_shared_autoindex)

    @cached_property
    def template_prefix(self):
        return self.blueprint.name + '/'


class AutoIndexModule(AutoIndexBlueprint):
    """Deprecated module support.

    .. versionchanged:: 0.3.1
       ``AutoIndexModule`` was deprecated. Use ``AutoIndexBlueprint`` instead.
    """

    def __init__(self, *args, **kwargs):
        import warnings
        warnings.warn('AutoIndexModule is deprecated; ' \
                      'use AutoIndexBlueprint instead.', DeprecationWarning)
        super(AutoIndexModule, self).__init__(*args, **kwargs)

    @property
    def mod(self):
        return self.blueprint
