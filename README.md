Flask-AutoIndex

A mod_autoindex for Flask

## Requirements

* Flask
* Python 3

## Usage

```
import os.path
from flask import Flask
from flask_autoindex import AutoIndex

app = Flask(__name__)
AutoIndex(app, browse_root=os.path.curdir)

if __name__ == '__main__':
    app.run()
```

## Test

`python setup.py test`