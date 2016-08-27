import os.path
from flask import Flask
from flask_autoindex import AutoIndex


app = Flask(__name__)
AutoIndex(app)

if __name__ == '__main__':
    app.run()
