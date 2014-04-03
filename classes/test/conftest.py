# -*- coding: utf-8 -*-
import os.path
import pytest
import json
from classes.knparam import *
from classes.knpage import *
from classes.knkoma import *
from classes.knbook import *
from classes.knutil import *

DATA_DIR = '/home/skkmania/mnt2/workspace/pysrc/knbnk/data'


def pytest_funcarg__knp(request):
    bookId = '1091460'
    params = {
        "bookId":      "1091460",
        "datadir":     '/home/skkmania/mnt2/workspace/pysrc/knbnk/data',
        "paramfdir":   "/".join([DATA_DIR, bookId]),
        "workdir":     "/".join([DATA_DIR, bookId]),
        "outdir":      "/".join([DATA_DIR, bookId]),
        "paramfname":  "/".join([DATA_DIR, bookId, "knbk1.json"]),
        "logfilename": "/".join([DATA_DIR, bookId, "knbk1.log"]),
        "tmpl": {
            "koma": {
                "scale_size":   640.0,
                "boundingRect": [16, 32],
                "mode":         "EXTERNAL",
                "method":       "NONE",
                "hough":        [1, 2, 100],
                "canny":        [50, 200, 3],
                "imgfname":     "/".join([DATA_DIR, bookId, "t.jpeg"]),
                "outdir":       "/".join([DATA_DIR, bookId]),
                "paramfname":   "/".join([DATA_DIR, bookId, "twletters_01.json"]),
                "outfilename":  "twl_can_50_200_hough_1_2_100"
            },
            "page": {
            },
            "layout": {
            },
            "char": {
            }
        },
        "spec": {
            "001": {
                "imgfname":     "/".join([DATA_DIR, bookId, "001.jpeg"]),
                "0": {
                    "imgfname":     "/".join([DATA_DIR, bookId, "001_0.jpeg"]),
                },
                "1": {
                    "imgfname":     "/".join([DATA_DIR, bookId, "001_1.jpeg"]),
                },
            },
            "002": {
                "0": {},
                "1": {}
            },
            "003": {
                "0": {},
                "1": {}
            }
        }
    }
    check_test_environment(params, bookId)
    return KnParam(param_fname=params['paramfname'])


def pytest_funcarg__knpd(request):
    bookId = '1091460'
    params = {
        "bookId":      "1091460",
        "datadir":     '/home/skkmania/mnt2/workspace/pysrc/knbnk/data',
        "paramfdir":   "/".join([DATA_DIR, bookId]),
        "workdir":     "/".join([DATA_DIR, bookId]),
        "outdir":      "/".join([DATA_DIR, bookId]),
        "paramfname":  "/".join([DATA_DIR, bookId, "knbk1.json"]),
        "logfilename": "/".join([DATA_DIR, bookId, "knbk1.log"]),
        "tmpl": {
            "koma": {
                "scale_size":   640.0,
                "boundingRect": [16, 32],
                "mode":         "EXTERNAL",
                "method":       "NONE",
                "hough":        [1, 2, 100],
                "canny":        [50, 200, 3],
                "imgfname":     "/".join([DATA_DIR, bookId, "t.jpeg"]),
                "outdir":       "/".join([DATA_DIR, bookId]),
                "paramfname":   "/".join([DATA_DIR, bookId, "twletters_01.json"]),
                "outfilename":  "twl_can_50_200_hough_1_2_100"
            },
            "page": {
            },
            "layout": {
            },
            "char": {
            }
        },
        "spec": {
            "001": {
                "imgfname":     "/".join([DATA_DIR, bookId, "001.jpeg"]),
                "0": {
                    "imgfname":     "/".join([DATA_DIR, bookId, "001_0.jpeg"]),
                },
                "1": {
                    "imgfname":     "/".join([DATA_DIR, bookId, "001_1.jpeg"]),
                },
            },
            "002": {
                "0": {},
                "1": {}
            },
            "003": {
                "0": {},
                "1": {}
            }
        }
    }
    check_test_environment(params, bookId)
    return KnParam(param_dict=params)

def pytest_funcarg__kn(request):
    bookId = 'twletters'
    params = {
        "scale_size":   640.0,
        "boundingRect": [16, 32],
        "mode":         "EXTERNAL",
        "method":       "NONE",
        "hough":        [1, 2, 100],
        "canny":        [50, 200, 3],
        "imgfname":     "/".join([DATA_DIR, bookId, "twletters.jpg"]),
        "outdir":       "/".join([DATA_DIR, bookId]),
        "paramfname":   "/".join([DATA_DIR, bookId, "twletters_01.json"]),
        "outfilename":  "twl_can_50_200_hough_1_2_100"
    }
    check_test_environment(params, bookId)
    return KnPage(params=params['paramfname'])


def pytest_funcarg__kn005(request):
    bookId = 'twletters'
    params = {
        "scale_size":   640.0,
        "boundingRect": [16, 32],
        "mode":         "EXTERNAL",
        "method":       "NONE",
        "canny":        [100, 200, 3],
        "imgfname":     "/".join([DATA_DIR, bookId, "005.jpeg"]),
        "outdir":       "/".join([DATA_DIR, bookId]),
        "paramfname":   "/".join([DATA_DIR, bookId, "twletters_04.json"]),
        "outfilename":  "twl_can_100_200"
    }
    check_test_environment(params, bookId)
    return KnPage(params=params['paramfname'])


def pytest_funcarg__knbk1(request):
    bookId = '1091460'
    params = {
        "bookId":      "1091460",
        "arcpath":     "/".join([DATA_DIR, bookId + '.tar.bz2']),
        "outdir":      "/".join([DATA_DIR, bookId]),
        "workdir":      "/".join([DATA_DIR, bookId]),
        "paramfdir":      "/".join([DATA_DIR, bookId]),
        "paramfname":  "/".join([DATA_DIR, bookId, "knbk1.json"]),
        "logfilename":  "/".join([DATA_DIR, bookId, "knbk1.log"])
    }
    check_test_environment(params, bookId)
    return KnBook(param_fname=params['paramfname'])


def pytest_funcarg__twl(request):
    bookId = 'twletters'
    params = {
        "scale_size":   640.0,
        "boundingRect": [16, 32],
        "mode":         "EXTERNAL",
        "method":       "NONE",
        "canny":        [50, 200, 3],
        "hough":        [1, 2, 100],
        "imgfname":     "/".join([DATA_DIR, bookId, "twletters.jpg"]),
        "outfilename":  "twl_can_50_200_hough_1_2_100",
        "paramfname":   "/".join([DATA_DIR, bookId, "twletters_01.json"]),
        "outdir":       "/".join([DATA_DIR, bookId])
    }
    check_test_environment(params, bookId)
    return KnPage(params=params['paramfname'])


def pytest_runtest_setup(item):
    pass


def pytest_collect_file(parent, path):
    if path.ext == ".yml" and path.basename.startswith("test"):
        return YamlFile(path, parent)


class YamlFile(pytest.File):
    def collect(self):
        import yaml  # we need a yaml parser, e.g. PyYAML
        raw = yaml.safe_load(self.fspath.open())
        for name, spec in raw.items():
            yield YamlItem(name, self, spec)


class YamlItem(pytest.Item):
    def __init__(self, name, parent, spec):
        super(YamlItem, self).__init__(name, parent)
        self.spec = spec

    def runtest(self):
        for name, value in self.spec.items():
            # some # custom # test # execution
            # (dumb # example # follows)
            if name != value:
                raise YamlException(self, name, value)

    def repr_failure(self, excinfo):
        """ called when self.runtest() raises an exception. """
        if isinstance(excinfo.value, YamlException):
            return "\n".join([
                "usecase execution failed",
                "   spec failed: %r: %r" % excinfo.value.args[1:3],
                "   no further details known at this point."
            ])

    def reportinfo(self):
        return self.fspath, 0, "usecase: %s" % self.name


class YamlException(Exception):
    """ custom exception for error reporting. """
