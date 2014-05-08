# -*- coding: utf-8 -*-
#import os.path
import pytest
import copy
#import json
from classes.knparam import KnParam
import classes.knutil as ku

DATA_DIR = '/home/skkmania/mnt2/workspace/pysrc/knbnk/data'


Default_Param = {
    "param": {
        "arcdir":      DATA_DIR,
        "workdir":     DATA_DIR
    },
    "book": {
        "height":       600,
        "width":        400,
        "pages_in_koma": 2,
        "dan":          1,
        "vorh":         "vert",
        "keisen":       "no",
        "waku":         "yes"
    },
    "koma": {
        "scale_size":   640.0,
        "hough":        [1, 2, 100],
        "canny":        [50, 200, 3],
    },
    "page": {
        "pagedir":      "/".join(['can_50_200_3', 'hgh_1_2_100', 'right']),
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


def pytest_funcarg__knp(request):
    param_dict = copy.deepcopy(Default_Param)
    spec = {
        "param": {
            "logfilename": "kn021",
            "arcdir":      DATA_DIR,
            "outdir":      "/".join([DATA_DIR, "1091460"]),
            "workdir":     DATA_DIR,
            "paramfdir":   "1091460",
            "paramfname":  "knp.json",
            "balls":       ["1091460"]
        },
        "book": {
            "bookdir":      '1091460',
            "bookId":       "1091460"
        },
        "koma": {
            "komadir":      'k001',
            "komaId":       1,
            "komaIdStr":    "001",
            "imgfname":     "001.jpeg"
        },
        "page": {
            "imgfname":     "001_0.jpeg"
        }
    }
    for k, v in param_dict.items():
        v.update(spec[k])
    ku.check_test_environment(param_dict, '1091460')
    return KnParam(param_dict)


def pytest_funcarg__kn005(request):
    param_dict = copy.deepcopy(Default_Param)
    spec = {
        "param": {
            "logfilename": "kn005",
            "arcdir":      DATA_DIR,
            "outdir":      "/".join([DATA_DIR, "twletters"]),
            "workdir":     DATA_DIR,
            "paramfdir":   "twletters",
            "paramfname":  "twlkn005.json",
            "balls":       ["twletters"]
        },
        "book": {
            "bookdir":      "twletters",
            "bookId":       "twletters"
        },
        "koma": {
            "komadir":      'k005',
            "komaId":       5,
            "komaIdStr":    "005",
            "imgfname":     "005.jpeg"
        },
        "page": {
            "imgfname":     "005_0.jpeg"
        }
    }
    for k, v in param_dict.items():
        v.update(spec[k])
    ku.check_test_environment(param_dict, 'twletters')
    return KnParam(param_dict)


def pytest_funcarg__knManyLines(request):
    param_dict = copy.deepcopy(Default_Param)
    spec = {
        "param": {
            "logfilename": "knM007",
            "arcdir":      DATA_DIR,
            "outdir":      "/".join([DATA_DIR, "1142178"]),
            "workdir":     DATA_DIR,
            "paramfdir":   "1142178",
            "paramfname":  "knMany007.json",
            "balls":       ["1142178"]
        },
        "book": {
            "bookdir":      "1142178",
            "bookId":       "1142178"
        },
        "koma": {
            "scale_size":   320.0,
            "hough": [1, 2, 80],
            "canny": [50, 150, 3],
            "komadir":      'k007',
            "komaId":       7,
            "komaIdStr":    "007",
            "imgfname":     "007.jpeg",
            "small_zone_levels": {'upper':  [0.03, 0.1],
                                  'lower':  [0.9, 0.97],
                                  'center': [0.45, 0.55],
                                  'left':   [0.03, 0.12],
                                  'right':  [0.88, 0.97]}
        },
        "page": {
            "imgfname":     "007_0.jpeg"
        }
    }
    for k, v in param_dict.items():
        v.update(spec[k])
    ku.check_test_environment(param_dict, '1142178')
    return KnParam(param_dict)


def pytest_funcarg__knFewLines(request):
    param_dict = copy.deepcopy(Default_Param)
    spec = {
        "param": {
            "logfilename": "knF006",
            "arcdir":      DATA_DIR,
            "outdir":      "/".join([DATA_DIR, "1123003"]),
            "workdir":     DATA_DIR,
            "paramfdir":   "1123003",
            "paramfname":  "knMany006.json",
            "balls":       ["1123003"]
        },
        "book": {
            "bookdir":      "1123003",
            "bookId":       "1123003"
        },
        "koma": {
            "scale_size":   320.0,
            "hough": [1, 180, 200],
            "canny": [50, 150, 3],
            "komadir":      'k006',
            "komaId":       7,
            "komaIdStr":    "006",
            "imgfname":     "006.jpeg"
        },
        "page": {
            "imgfname":     "006_0.jpeg"
        }
    }
    for k, v in param_dict.items():
        v.update(spec[k])
    ku.check_test_environment(param_dict, '1123003')
    return KnParam(param_dict)


def pytest_funcarg__graph2(request):
    """
    両側とも全面挿絵のサンプル
    """
    param_dict = copy.deepcopy(Default_Param)
    spec = {
        "param": {
            "logfilename": "kngraph2_009",
            "arcdir":      DATA_DIR,
            "outdir":      "/".join([DATA_DIR, "graph2"]),
            "workdir":     DATA_DIR,
            "paramfdir":   "graph2",
            "paramfname":  "kngraph2.json",
            "balls":       ["graph2"]
        },
        "book": {
            "bookdir":      "graph2",
            "bookId":       "graph2"
        },
        "koma": {
            "komadir":      'k009',
            "komaId":       9,
            "komaIdStr":    "009",
            "imgfname":     "009.jpeg"
        },
        "page": {
            "imgfname":     "009_0.jpeg",
        }
    }
    for k, v in param_dict.items():
        v.update(spec[k])
    ku.check_test_environment(param_dict, 'graph2')
    return KnParam(param_dict)


def pytest_funcarg__b1g101(request):
    """
    両側とも全面挿絵のサンプル
    """
    param_dict = copy.deepcopy(Default_Param)
    spec = {
        "param": {
            "logfilename": "kn021",
            "arcdir":      DATA_DIR,
            "outdir":      "/".join([DATA_DIR, "b1g101"]),
            "workdir":     DATA_DIR,
            "paramfdir":   "b1g101",
            "paramfname":  "b1g101.json",
            "balls":       ["b1g101"]
        },
        "book": {
            "bookdir":      'b1g101',
            "bookId":       "b1g101",
        },
        "koma": {
            "komadir":      'k021',
            "komaId":       21,
            "komaIdStr":    "021",
            "imgfname":     "021.jpeg"
        },
        "page": {
            "imgfname":     "021_0.jpeg",
        }
    }
    for k, v in param_dict.items():
        v.update(spec[k])
    ku.check_test_environment(param_dict, 'b1g101')
    return KnParam(param_dict)


def pytest_funcarg__b1g102(request):
    """
    両側とも全面挿絵のサンプル
    """
    param_dict = copy.deepcopy(Default_Param)
    spec = {
        "param": {
            "logfilename": "kn106",
            "arcdir":      DATA_DIR,
            "outdir":      "/".join([DATA_DIR, "b1g102"]),
            "workdir":     DATA_DIR,
            "paramfdir":   "b1g102",
            "paramfname":  "b1g102.json",
            "balls":       ["b1g102"]
        },
        "book": {
            "bookdir":      "b1g102",
            "bookId":       "b1g102"
        },
        "koma": {
            "komadir":      'k106',
            "komaId":       106,
            "komaIdStr":    "106",
            "imgfname":     "106.jpeg"
        },
        "page": {
            "imgfname":     "106_0.jpeg"
        }
    }
    for k, v in param_dict.items():
        v.update(spec[k])
    ku.check_test_environment(param_dict, 'b1g102')
    return KnParam(param_dict)


def pytest_funcarg__knbk1(request):
    param_dict = copy.deepcopy(Default_Param)
    spec = {
        "param": {
            "logfilename": "knbk1",
            "arcdir":      DATA_DIR,
            "outdir":      "/".join([DATA_DIR, "1091460"]),
            "workdir":     DATA_DIR,
            "paramfdir":   "1091460",
            "paramfname":  "knbk1.json",
            "balls":       ["1091460"]
        },
        "book": {
            "bookdir":      "1091460",
            "bookId":       "1091460"
        },
        "koma": {
            "komadir":      'k001',
            "komaId":       1,
            "komaIdStr":    "001",
            "imgfname":     "001.jpeg"
        },
        "page": {
            "imgfname":     "001_0.jpeg"
        }
    }
    for k, v in param_dict.items():
        v.update(spec[k])
    ku.check_test_environment(param_dict, "1091460")
    return KnParam(param_dict)


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
