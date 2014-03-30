# -*- coding: utf-8 -*-
# params_file の書式 :  json text
#   {
#     以下は必須
#     "bookId":        Integer                  #  NDLの識別子からとった数値
#     "arcpath":       bookのtar ballのfull path
#     "outdir":        bookのfileを展開するディレクトリ
#     "paramfname"   : "string"                 # parameter file name
#                             (つまりこのfile自身のfull path)
#     以下は任意
#   }
from .knkoma import *
from .knpage import *
from .knutil import read_params
import os.path

__all__ = ["KnBook", "KnBookException", "KnBookParamsException"]
DATA_DIR = '/home/skkmania/mnt2/workspace/pysrc/knbnk/data'


class KnBookException(Exception):
    def __init__(self, value):
        if value is None:
            self.initException()
        else:
            self.value = value

    def __str__(self):
        return repr(self.value)

    def printException(self):
        print "KnBook Exception."

    @classmethod
    def paramsFileNotFound(self, value):
        print '%s not found.' % value

    @classmethod
    def initException(self):
        print "parameter file name must be specified."


class KnBookParamsException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class KnBook:
    def __init__(self, fname=None, datadir=None, params=None, outdir=None):
        if params is None:
            raise KnBookException('params is None')

        if os.path.exists(params):
            read_params(self, params)
            self.expand()
        else:
            raise KnBookParamsException(params)
            # raise KnBookException.paramsFileNotFound(params)

    def expand(self):
        pass
