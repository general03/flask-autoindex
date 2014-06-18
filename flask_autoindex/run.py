import os.path
from flask import Flask
from flask.ext.autoindex import AutoIndex


def run():
    app = Flask(__name__)
    AutoIndex(app, browse_root=os.path.curdir)
    app.run()

if __name__ == '__main__':
    run()
