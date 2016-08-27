from __future__ import absolute_import
from future.builtins import bytes
import mimetypes
import os
import sys
import unittest

from flask import *
from flask_autoindex import *


__file__ = __file__.replace('.pyc', '.py')
browse_root = os.path.abspath(os.path.dirname(__file__))


if sys.version_info < (3,):
    b = lambda s: s
else:
    b = lambda s: bytes(s, 'ascii')


class RootDirectoryTestCase(unittest.TestCase):

    def setUp(self):
        self.rootdir = RootDirectory(browse_root)

    def test_root_dir(self):
        assert isinstance(self.rootdir, RootDirectory)
        assert self.rootdir.path == '.'
        assert os.path.samefile(self.rootdir.abspath, browse_root)
        assert os.path.isdir(self.rootdir.abspath)

    def test_init(self):
        assert isinstance(Directory(browse_root), RootDirectory)
        assert isinstance(Directory('.', self.rootdir), RootDirectory)
        assert isinstance(Entry(browse_root), RootDirectory)
        assert isinstance(Entry('.', self.rootdir), RootDirectory)

    def test_same_object(self):
        assert self.rootdir is RootDirectory(browse_root)
        assert self.rootdir is Directory(browse_root)
        assert self.rootdir is Directory('.', self.rootdir)
        assert self.rootdir is Entry(browse_root)
        assert self.rootdir is Entry('.', self.rootdir)
        assert RootDirectory(browse_root) is Directory(browse_root)
        assert RootDirectory(browse_root) is Entry('.', self.rootdir)
        assert Entry(browse_root) is Directory('.', self.rootdir)

    def test_get_child_file(self):
        file = self.rootdir.get_child('__init__.py')
        assert isinstance(file, File)
        assert file.ext == 'py'
        assert file.path == '__init__.py'
        assert file.rootdir is self.rootdir

    def test_get_child_dir(self):
        dir = self.rootdir.get_child('static')
        assert isinstance(dir, Directory)
        assert dir.path == 'static'
        assert dir.rootdir is self.rootdir

    def test_contain(self):
        assert 'static' in self.rootdir
        assert '__init__.py' in self.rootdir
        assert Entry('static', self.rootdir) in self.rootdir
        assert Entry('__init__.py', self.rootdir) in self.rootdir
        assert '^_^' not in self.rootdir


class DirectoryTestCase(unittest.TestCase):

    def setUp(self):
        self.rootdir = RootDirectory(browse_root)
        self.static = Directory('static', self.rootdir)

    def test_dir(self):
        assert isinstance(self.static, Directory)
        assert self.static.path == 'static'
        assert os.path.samefile(self.static.abspath,
                                os.path.join(browse_root, 'static'))
        assert os.path.isdir(self.static.abspath)

    def test_init(self):
        assert isinstance(Directory('static', self.rootdir), Directory)
        assert isinstance(Entry('static', self.rootdir), Directory)

    def test_same_object(self):
        assert self.static is Directory('static', self.rootdir)
        assert self.static is Entry('static', self.rootdir)
        assert Directory('static', self.rootdir) is \
               Entry('static', self.rootdir)
        assert self.static.parent is self.rootdir

    def test_get_child_file(self):
        file = self.static.get_child('test.txt')
        assert isinstance(file, File)
        assert file.ext == 'txt'
        assert file.path == 'static/test.txt'
        assert file.rootdir is self.rootdir

    def test_contain(self):
        assert 'test.py' in self.static
        assert Entry('static/test.py', self.rootdir) in self.static
        assert '^_^' not in self.static


class FileTestCase(unittest.TestCase):

    def setUp(self):
        self.rootdir = RootDirectory(browse_root)
        self.itself = File('__init__.py', self.rootdir)

    def test_file(self):
        assert isinstance(self.itself, File)
        assert self.itself.path == '__init__.py'
        assert os.path.samefile(self.itself.abspath,
                                os.path.join(browse_root, '__init__.py'))
        assert os.path.isfile(self.itself.abspath)

    def test_init(self):
        assert isinstance(File('__init__.py', self.rootdir), File)
        assert isinstance(Entry('__init__.py', self.rootdir), File)
        assert isinstance(File('static/test.txt', self.rootdir), File)
        assert isinstance(Entry('static/test.txt', self.rootdir), File)

    def test_same_object(self):
        assert self.itself is File('__init__.py', self.rootdir)
        assert self.itself is Entry('__init__.py', self.rootdir)
        assert File('__init__.py', self.rootdir) is \
               Entry('__init__.py', self.rootdir)

    def test_properties(self):
        with open(__file__) as f:
            source = ''.join(f.readlines())
        assert self.itself.data.strip() == source.strip()
        assert self.itself.size == len(source)
        assert self.itself.ext == 'py'
        assert self.itself.mimetype == mimetypes.guess_type(__file__)


class ApplicationTestCase(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app2 = Flask(__name__)
        self.idx = AutoIndex(self.app, browse_root, add_url_rules=True)
        self.idx2 = AutoIndex(self.app2, browse_root,
                              silk_options={'silk_path': '/myicons'})
        @self.app2.route('/')
        @self.app2.route('/<path:path>')
        def autoindex_test(path='.'):
            return self.idx2.render_autoindex(path, browse_root)

    def get(self, path):
        return self.app.test_client().get(path)

    def get2(self, path):
        self.app2.config['TESTING'] = True
        return self.app2.test_client().get(path)

    def test_css(self):
        for get in [self.get, self.get2]:
            rv = get('/__autoindex__/autoindex.css')
            assert 200 == rv.status_code

    def test_icon(self):
        rv = self.get('/__icons__/page_white.png')
        rv2 = self.get2('/myicons/page_white.png')
        assert 294 == len(rv.data)
        assert rv.data == rv2.data

    def test_autoindex(self):

        assert b('__init__.py') in self.get('/').data
        assert b('__init__.py') in self.get2('/').data

    def test_own_static_file(self):
        rv = self.get('/static/helloworld.txt')
        assert b('Hello, world!') == rv.data.strip()

    def test_own_page(self):
        for get in [self.get, self.get2]:
            rv = get('/test')
            assert not b('foo bar foo bar') == rv.data.strip()
        @self.app.route('/test')
        def sublee():
            return 'foo bar foo bar', 200
        @self.app2.route('/test')
        def sublee():
            return 'foo bar foo bar', 200
        for get in [self.get, self.get2]:
            rv = get('/test')
            assert b('foo bar foo bar') == rv.data.strip()

    def test_builtin_icon_rule(self):
        testset = {'7z': 'page_white_zip.png',
                   'avi': 'film.png',
                   'cer': 'key.png',
                   'html': 'page_white_code.png',
                   'iso': 'cd.png',
                   'rss': 'feed.png'}
        with self.app.test_request_context():
            for ext, icon in list(testset.items()):
                file = self.idx.rootdir.get_child('static/test.' + ext)
                assert file.guess_icon().endswith(icon)

    def test_custom_icon_rule(self):
        with self.app.test_request_context():
            file = self.idx.rootdir.get_child('__init__.py')
            original_icon_url = file.guess_icon()
            self.idx.add_icon_rule('table.png', ext='py')
            customized_icon_url = file.guess_icon()
            assert original_icon_url.endswith('page_white_python.png')
            assert customized_icon_url.endswith('table.png')


class SubdomainTestCase(unittest.TestCase):

    def setUp(self):
        from .blueprinttest import bp
        app = Flask(__name__)
        app.config['SERVER_NAME'] = 'example.org'
        AutoIndex(bp, browse_root)
        app.register_blueprint(bp, subdomain='test')
        self.app = app

    def get(self, path):
        return self.app.test_client().get(path, 'http://test.example.org/')

    def test_css(self):
        rv = self.get('/static/autoindex.css')
        assert 200 == rv.status_code, 'could not found preloaded css file.'

    def test_icon(self):
        rv = self.get('/__icons__/page_white.png')
        assert 294 == len(rv.data), 'could not found preloaded icon file.'

    def test_browse(self):
        rv = self.get('/')
        assert 'Index of /' in rv.data
        assert '__init__.py' in rv.data

    def test_own_static_file(self):
        rv = self.get('/static/helloworld.txt')
        assert 'Hello, world!' == rv.data.strip()


class WithoutSubdomainTestCase(unittest.TestCase):

    def setUp(self):
        from .blueprinttest import bp
        app = Flask(__name__)
        AutoIndex(bp, browse_root)
        app.register_blueprint(bp)
        self.app = app

    def get(self, path):
        return self.app.test_client().get(path)

    def test_css(self):
        rv = self.get('/static/autoindex.css')
        assert 200 == rv.status_code, 'could not found preloaded css file.'

    def test_icon(self):
        rv = self.get('/__icons__/page_white.png')
        assert 294 == len(rv.data), 'could not found preloaded icon file.'

    def test_browse(self):
        rv = self.get('/')
        assert 'Index of /' in rv.data
        assert '__init__.py' in rv.data


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(RootDirectoryTestCase))
    suite.addTest(unittest.makeSuite(DirectoryTestCase))
    suite.addTest(unittest.makeSuite(FileTestCase))
    suite.addTest(unittest.makeSuite(ApplicationTestCase))
    # These cases will be passed on Flask next generation.
    # suite.addTest(unittest.makeSuite(SubdomainTestCase))
    # suite.addTest(unittest.makeSuite(WithoutSubdomainTestCase))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
