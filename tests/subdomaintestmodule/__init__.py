import os.path
import sys
import flask
from flaskext.autoindex import AutoIndex


root = os.path.abspath(os.path.dirname(__file__))
mod = AutoIndex(__name__, root, name="test", subdomain="test")

