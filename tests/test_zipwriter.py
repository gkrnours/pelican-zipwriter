from __future__ import unicode_literals

from binascii import crc32
import filecmp
import locale
import logging
import os
import unittest
from shutil import rmtree
from tempfile import mkdtemp, mkstemp
from zipfile import ZipFile
from pelican.log import init
from pelican import Pelican
from pelican.settings import read_settings

CURRENT_DIR = os.path.dirname(__file__)
REF_PATH = os.path.join(CURRENT_DIR, "reference")
INPUT_PATH = os.path.join(CURRENT_DIR, "content")
OUTPUT_PATH = os.path.join(CURRENT_DIR, "output")
FILENAME = "archive.zip"


def cmpzip2dir(zipfile, dirpath):
    badapples = []
    for prefix, dirs, files in os.walk(dirpath):
        _dir = os.path.join('content', prefix[len(dirpath)+1:])
        for f in files:
            path = os.path.join(_dir, f)
            try:
                with open(os.path.join(prefix, f), 'rb') as f:
                    if zipfile.getinfo(path).CRC == crc32(f.read()):
                        print(".", end="")
                    else:
                        print("X", end="")
                        badapples.append(path)
            except KeyError:
                print("F", end="")
                badapples.append(path)
    print("")


class TestZipWriter(unittest.TestCase):
    def setUp(self):
        self.cache_tmp = mkdtemp(prefix="pelicancache.")
        self.old_locale = locale.setlocale(locale.LC_ALL)
        locale.setlocale(locale.LC_ALL, str('C'))

    def tearDown(self):
        rmtree(self.cache_tmp)
        locale.setlocale(locale.LC_ALL, self.old_locale)
        super(TestZipWriter, self).tearDown()

    def _test_run_without_output_file(self):
        import pelicanzipwriter
        settings = read_settings(path=None, override={
            "PATH": INPUT_PATH,
            "OUTPUT_PATH": mkdtemp(),
            "CACHE_PATH": self.cache_tmp,
            "PLUGINS": [pelicanzipwriter],
            "TIMEZONE": 'UTC',
            "SITEURL": 'example.com',
        })
        Pelican(settings=settings).run()

    def test_run_with_output_file(self):
        import pelicanzipwriter
        settings = read_settings(path=None, override={
            "PATH": INPUT_PATH,
            "OUTPUT_FILE": os.path.join(OUTPUT_PATH, FILENAME),
            "OUTPUT_PATH": OUTPUT_PATH,
            "CACHE_PATH": self.cache_tmp,
            "PLUGINS": [pelicanzipwriter],
            "TIMEZONE": 'UTC',
            "SITEURL": 'example.com',
        })
        Pelican(settings=settings).run()
        cmpzip2dir(ZipFile(os.path.join(OUTPUT_PATH, FILENAME)), REF_PATH)

    def test_with_file_object_as_input(self):
        import pelicanzipwriter
        fd, path = mkstemp(dir=OUTPUT_PATH, prefix="archive_", suffix=".zip")
        f = os.fdopen(fd, 'wb')
        settings = read_settings(path=None, override={
            "PATH": INPUT_PATH,
            "OUTPUT_FILE": f,
            "OUTPUT_PATH": "content",
            "CACHE_PATH": self.cache_tmp,
            "PLUGINS": [pelicanzipwriter],
            "TIMEZONE": 'UTC',
            "SITEURL": 'example.com',
        })
        Pelican(settings=settings).run()
        f.close()

