from mimetypes import guess_type
from fnmatch import fnmatch
from .entry import File, Folder, Default


by_extension = [
    ("page_white_python.png", "py"),
    ("python.png", "pyc"),
    ("page_white_text_width.png", ["md", "markdown", "rst", "rtf"]),
    ("page_white_code.png", ["html", "htm", "cgi"]),
    ("page_white_visualstudio.png", ["asp", "vb"]),
    ("page_white_ruby.png", "rb"),
    ("page_code.png", "xhtml"),
    ("page_white_code_red.png", ["xml", "xsl", "xslt", "yml"]),
    ("script.png", ["js", "json", "applescript", "htc"]),
    ("layout.png", ["css", "less"]),
    ("page_white_php.png", "php"),
    ("page_white_c.png", "c"),
    ("page_white_cplusplus.png", "cpp"),
    ("page_white_h.png", "h"),
    ("database.png", ["db", "sqlite", "sqlite3"]),
    ("page_white_database.png", "sql"),
    ("page_white_gear.png", ["conf", "cfg", "ini", "reg", "sys"]),
    ("page_white_zip.png", ["zip", "tar", "gz", "tgz", "7z", "alz", "rar", \
                            "bin", "cab"]),
    ("cup.png", "jar"),
    ("page_white_cup.png", ["java", "jsp"]),
    ("application_osx_terminal.png", "sh"),
    ("page_white_acrobat.png", "pdf"),
    ("package.png", ["pkg", "dmg"]),
    ("shape_group.png", ["ai", "svg", "eps"]),
    ("application_osx.png", "app"),
    ("cursor.png", "cur"),
    ("feed.png", "rss"),
    ("cd.png", ["iso", "vcd", "toast"]),
    ("page_white_powerpoint.png", ["ppt", "pptx"]),
    ("page_white_excel.png", ["xls", "xlsx", "csv"]),
    ("page_white_word.png", ["doc", "docx"]),
    ("page_white_flash.png", "swf"),
    ("page_white_actionscript.png", ["fla", "as"]),
    ("comment.png", "smi"),
    ("disk.png", ["bak", "bup"]),
    ("application_xp_terminal.png", ["bat", "com"]),
    ("application.png", "exe"),
    ("key.png", "cer"),
    ("cog.png", ["dll", "so"]),
    ("pictures.png", "ics"),
    ("error.png", "log"),
    ("music.png", "mpa"),
    ("font.png", ["ttf", "eot"]),
    ("vcard.png", "vcf"),
    ("page_white.png", Default)
]

by_filename = [
    ("page_white_gear.png", ["Makefile", "Rakefile"])
]

by_mimetype = [
    ("page_white_text.png", "text/*"),
    ("picture.png", "image/*"),
    ("music.png", "audio/*"),
    ("film.png", "video/*")
]


def make_extension_rule(ext):
    if isinstance(ext, basestring):
        return lambda ent: ent.ext == ext
    elif getattr(ext, "__iter__", False):
        return lambda ent: ent.ext in ext

def make_filename_rule(name):
    if isinstance(name, basestring):
        return lambda ent: ent.name == name
    elif getattr(name, "__iter__", False):
        return lambda ent: ent.name in name

def make_mimetype_rule(mimetype):
    rule = lambda ent: fnmatch(guess_type(ent.name)[0] or "", mimetype)
    if isinstance(mimetype, basestring):
        return rule
    elif getattr(mimetype, "__iter__", False):
        return lambda ent: all(map(rule, mimetype))


for icon, ext in by_extension:
    rule = make_extension_rule(ext)
    if rule:
        File.add_icon_rule(icon, rule)

for icon, name in by_filename:
    rule = make_filename_rule(name)
    if rule:
        File.add_icon_rule(icon, rule)

for icon, mimetype in by_mimetype:
    rule = make_mimetype_rule(mimetype)
    if rule:
        File.add_icon_rule(icon, rule)

