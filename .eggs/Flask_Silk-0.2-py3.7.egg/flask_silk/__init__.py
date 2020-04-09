# -*- coding: utf-8 -*-
"""
    flask_silk
    ~~~~~~~~~~

    A small extension for adding `Silk
    <http://www.famfamfam.com/lab/icons/silk/>`_ icons.

    :copyright: (c) 2010-2013 by Heungsub Lee.
    :license: BSD, see LICENSE for more details.
"""
import os

from flask import send_from_directory


__version__ = '0.2'
__all__ = ['Silk', 'send_silkicon']


class Silk(object):
    """This small extension adds :meth:`silkicon` to your Flask application::

        from flask import Flask
        from flask.ext.silk import Silk
        app = Flask(__name__)
        silk = Silk(app)

    Or it works with your Flask blueprint::

        from flask import Blueprint
        from flask.ext.silk import Silk
        blu = Blueprint(__name__, __name__)
        silk = Silk(blu)

    Now the application or blueprint's ``/icons/<filaname>`` is bound to
    :meth:`silkicon` for serves a prepared silk icon.

    Also you can work with your own icon directory::

        import os.path
        my_icons = os.path.join(silk.base.static_path, 'icons')
        my_icons2 = os.path.join(silk.base.static_path, 'other-icons')
        silk.register_icon_directory(my_icons)
        silk.register_icon_directory(my_icons2)

    Silk finds the icon in the registered directories first. If the icon does
    not exist in any directories, Silk finds the prepared silk icon.

    :param base: the flask application or blueprint.
    :param silk_path: the path to serve silk icons. Defaults to ``/icons``.
    """

    directories = []

    def __init__(self, base, silk_path='/icons'):
        self.base = base
        if not silk_path.startswith('/'):
            silk_path = '/' + silk_path
        rule = silk_path + '/<filename>'
        self.silkicon = self.base.route(rule)(self.silkicon)

    def register_icon_directory(self, path):
        self.directories.append(path)

    def silkicon(self, filename):
        return send_silkicon(filename, directories=self.directories)


def send_silkicon(filename, directories=[]):
    """Sends an icon. The icon is in a shared directory or specified
    directories. Here's a simple examples of how to send an icon::

        from flask.ext.silk import send_silkicon
        from myapplication import app

        my_icons = os.path.join(app.static_path, 'icons')
        my_icons2 = os.path.join(app.static_path, 'other-icons')

        @app.route('/static/icons/<filename>')
        def icon(filename):
            return send_silkicon(filename, directories=[my_icons, my_icons2])

    :param filename: the filename for icon.
    :param directories: specified icon directories.
    """
    for directory in directories:
        try:
            return send_from_directory(directory, filename)
        except Exception:
            pass
    directory = os.path.join(os.path.dirname(__file__), 'icons')
    return send_from_directory(directory, filename)
