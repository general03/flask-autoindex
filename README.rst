Flask-AutoIndex
~~~~~~~~~~~~~~~

Generates index page like mod_autoindex. Under development.

Usage
=====

If you want to browse your ``public_html`` folder, follow these::

   import os.path
   import flask
   from flaskext.autoindex import AutoIndex


   public_html = os.path.join(os.path.expanduser("~"), "public_html")
   browse = AutoIndex(__name__, browse_root=public_html)

