# -*- coding: utf-8 -*-
#import os.path
import pytest
#import json
from classes.knparam import KnParam
from classes.knpage import KnPage
#from classes.knkoma import KnKoma
from classes.knbook import KnBook
import classes.knutil as ku

DATA_DIR = '/home/skkmania/mnt2/workspace/pysrc/knbnk/data'


def pytest_funcarg__knp(request):
    bookId = '1091460'
    params = {
        "param": {
            "arcdir":      DATA_DIR,
            "outdir":      "/".join([DATA_DIR, bookId]),
            "workdir":     DATA_DIR,
            "paramfdir":   DATA_DIR,
            "paramfname":  "/".join([DATA_DIR, "knp.json"]),
            "logfilename": "/".join([DATA_DIR, "knp"]),
            #"balls":       ["1123003", "1142178", "1092905"]
            "balls":       ["1741797", "1720450"]
        },
        "book": {
            "bookdir":      "/".join([DATA_DIR, bookId]),
            "bookId":       "1091460",
        },
        "koma": {
            "komadir":      "/".join([DATA_DIR, bookId, 'k001']),
            "komaId":       1,
            "komaIdStr":    "001",
            "scale_size":   640.0,
            "hough":        [1, 2, 100],
            "canny":        [50, 200, 3],
            "imgfname":     "001.jpeg"
        },
        "page": {
            "pagedir":      "/".join([DATA_DIR, bookId, 'k001',
                                      'can_50_200',
                                      'hgh_1_2_100', 'right']),
            "imgfname":     "001_0.jpeg",
            "lr":           "right",
            "mavstd":       10,
            "pgmgn":        [0.05, 0.05],
            "ismgn":        [15, 5],
            "toobig":       [200, 200],
            "boundingRect": [16, 32],
            "mode":         "EXTERNAL",
            "method":       "NONE",
            "canny":        [50, 200, 3]
        },
        "layout": {
        },
        "char": {
        }
    }
    ku.check_test_environment(params, bookId)
    return KnParam(param_fname=params['param']['paramfname'])


def pytest_funcarg__knpd(request):
    bookId = '1091460'
    params = {
        "param": {
            "arcdir":      DATA_DIR,
            "outdir":      "/".join([DATA_DIR, bookId]),
            "workdir":     DATA_DIR,
            "paramfdir":   DATA_DIR,
            "paramfname":  "/".join([DATA_DIR, "knbk1.json"]),
            "logfilename": "/".join([DATA_DIR, bookId, "knbk1"]),
            "balls":       ["1091460"]
        },
        "book": {
            "bookdir":      "/".join([DATA_DIR, bookId]),
            "bookId":       "1091460",
        },
        "koma": {
            "komadir":      "/".join([DATA_DIR, bookId, 'k001']),
            "komaId":       1,
            "komaIdStr":    "001",
            "scale_size":   640.0,
            "hough":        [1, 2, 100],
            "canny":        [50, 200, 3],
            "imgfname":     "/".join([DATA_DIR, bookId, "001.jpeg"]),
        },
        "page": {
            "pagedir":      "/".join([DATA_DIR, bookId, 'k001',
                                      'can_50_200',
                                      'hgh_1_2_100', 'right']),
            "imgfname":     "/".join([DATA_DIR, bookId,
                                      "pagedir", "001_0.jpeg"]),
            "lr": "right",
            "boundingRect": [16, 32],
            "mode":         "EXTERNAL",
            "method":       "NONE",
        },
        "layout": {
        },
        "char": {
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
    ku.check_test_environment(params, bookId)
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
    ku.check_test_environment(params, bookId)
    return KnPage(params=params['param']['paramfname'])


def pytest_funcarg__kn005(request):
    param_dict = {
        "param": {
            "outdir":       "/".join([DATA_DIR, 'twletters']),
            "paramfname":   "/".join([DATA_DIR, "kn005.json"]),
            "logfilename": "/".join([DATA_DIR, "kn005"]),
            "arcdir":      DATA_DIR,
            "outdir":      "/".join([DATA_DIR, "twletters"]),
            "workdir":     DATA_DIR,
            "paramfdir":   DATA_DIR,
            "paramfname":  "/".join([DATA_DIR, "knp.json"]),
            "balls":       ["twletters"]
        },
        "book": {
            "bookdir":      "/".join([DATA_DIR, 'twletters']),
            "bookId":       "twletters",
        },
        "koma": {
            "scale_size":   640.0,
            "imgfname":     "/".join([DATA_DIR, 'twletters', "005.jpeg"]),
            "komadir":      "/".join([DATA_DIR, 'twletters', 'k005']),
            "komaId":       5,
            "komaIdStr":    "005",
            "scale_size":   640.0,
            "hough":        [1, 2, 100],
            "canny":        [50, 200, 3],
            "imgfname":     "005.jpeg"
        },
        "page": {
            "pagedir":      "/".join([DATA_DIR, 'twletters', 'k005',
                                      'can_50_200',
                                      'hgh_1_2_100', 'right']),
            "imgfname":     "005_0.jpeg",
            "lr":           "right",
            "mavstd":       10,
            "pgmgn":        [0.05, 0.05],
            "ismgn":        [5, 0],
            "toobig":       [200, 200],
            "mcbs":         10,  # minimum collected box size
            "boundingRect": [16, 32],
            "mode":         "EXTERNAL",
            "method":       "NONE",
            "canny":        [50, 200, 3]
        }
    }
    ku.check_test_environment(param_dict, 'twletters')
    return KnPage(KnParam(param_dict))


def pytest_funcarg__graph(request):
    param_dict = {
        "param": {
            "outdir":       "/".join([DATA_DIR, 'graph']),
            "paramfname":   "/".join([DATA_DIR, "kn009.json"]),
            "logfilename": "/".join([DATA_DIR, "kn009"]),
            "arcdir":      DATA_DIR,
            "outdir":      "/".join([DATA_DIR, "graph"]),
            "workdir":     DATA_DIR,
            "paramfdir":   DATA_DIR,
            "paramfname":  "/".join([DATA_DIR, "knp.json"]),
            "balls":       ["graph"]
        },
        "book": {
            "bookdir":      "/".join([DATA_DIR, 'graph']),
            "bookId":       "graph",
        },
        "koma": {
            "scale_size":   640.0,
            "imgfname":     "/".join([DATA_DIR, 'graph', "009.jpeg"]),
            "komadir":      "/".join([DATA_DIR, 'graph', 'k009']),
            "komaId":       5,
            "komaIdStr":    "009",
            "scale_size":   640.0,
            "hough":        [1, 2, 100],
            "canny":        [50, 200, 3],
            "imgfname":     "009.jpeg"
        },
        "page": {
            "pagedir":      "/".join([DATA_DIR, 'graph', 'k009',
                                      'can_50_200',
                                      'hgh_1_2_100', 'right']),
            "imgfname":     "009_0.jpeg",
            "lr":           "right",
            "mavstd":       10,
            "pgmgn":        [0.05, 0.05],
            "ismgn":        [15, 5],
            "toobig":       [200, 200],
            "boundingRect": [16, 32],
            "mode":         "EXTERNAL",
            "method":       "NONE",
            "canny":        [50, 200, 3]
        }
    }
    ku.check_test_environment(param_dict, 'graph')
    return KnPage(KnParam(param_dict))


def pytest_funcarg__knbk1(request):
    DATA_DIR = '/home/skkmania/mnt2/workspace/pysrc/knbnk/data'
    bookId = '1091460'
    params = {
        "param": {
            "arcdir":      DATA_DIR,
            "outdir":      "/".join([DATA_DIR, bookId]),
            "workdir":     DATA_DIR,
            "paramfdir":   DATA_DIR,
            "paramfname":  "/".join([DATA_DIR, "knbk1.json"]),
            "logfilename": "/".join([DATA_DIR, bookId, "knbk1.log"]),
            "balls":       ["1091460"]
        },
        "book": {
            "bookdir":      "/".join([DATA_DIR, bookId]),
            "bookId":       "1091460",
        },
        "koma": {
            "komadir":      "/".join([DATA_DIR, bookId, 'k001']),
            "komaId":       1,
            "komaIdStr":    "001",
            "scale_size":   640.0,
            "hough":        [1, 2, 100],
            "canny":        [50, 200, 3],
            "imgfname":     "/".join([DATA_DIR, bookId, "001.jpeg"]),
        },
        "page": {
            "pagedir":      "/".join([DATA_DIR, bookId, 'k001',
                                      'can_50_200',
                                      'hgh_1_2_100', 'right']),
            "imgfname":     "/".join([DATA_DIR, bookId,
                                      "pagedir", "001_0.jpeg"]),
            "lr": "right",
            "boundingRect": [16, 32],
            "mode":         "EXTERNAL",
            "method":       "NONE",
        },
        "layout": {
        },
        "char": {
        }
    }
    ku.check_test_environment(params, bookId)
    param = KnParam(param_fname=params['param']['paramfname'])
    return KnBook(param)


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
