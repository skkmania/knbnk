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
import knkoma as kk
import knparam as kr
from .knutil import *
import os.path
import json

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
    def __init__(self, param=None, param_fname=None):
        print param_fname
        if param is None and param_fname is None:
            raise KnBookException('param or param_fname must be given.')

        if isinstance(param, kr.KnParam):
            self.param = param
        elif os.path.exists(param_fname):
            self.param = kr.KnParam(param_fname=param_fname)
        else:
            raise KnBookparam_fnameException(param_fname)
        self.expand()
        self.read_metadata()
        self.komas = []

    def expand(self):
        if not os.path.exists(self.param.outdir()):
            cmd = 'tar jxf %s/%s.tar.bz2 -C %s' % (
                self.param.datadir(), self.param.bookId(),
                self.param.workdir())
            os.system(cmd)
            cmd = "find %s -type d -name '*%s*' -exec mv {} %s \\;" %\
                (self.param.datadir(), self.param.bookId(),
                 self.param.workdir())
            os.system(cmd)

    def read_metadata(self):
        self.metafname = (self.param.workdir()
                          + '/raw_' + self.param.bookId() + '.json')
        if os.path.exists(self.metafname):
            with open(self.metafname) as f:
                lines = f.readlines()
                self.metadata = json.loads(''.join(lines))
                self.komanum = int(self.metadata['lastContentNo'])

    def divide_all(self):
        """
        book内の全コマをdivideする
        全コマのObjectをself.komasに保存する。
        (なので、コマ数が少ないときだけ実行すること。)
        """
        for k in range(1, self.komanum + 1):
            koma = kk.KnKoma(param=self.param)
            koma.divide(k)
            self.komas.append(koma)

    def divide_a_koma(self, komanum):
        """
        book内のコマのうち、komanumで指定した番号のコマをdivideする
        コマのObjectは保存しない。
        戻り値：KnPage objectのtuple(leftPage, rightPage)
        """
        koma = kk.KnKoma(param=self.param, komanum=komanum)
        return koma.divide()

    def collect_all(self):
        for k in self.komas:
            for p in k.pages:
                p.collect_boxes()

    def layout_all(self):
        for k in self.komas:
            for p in k.pages:
                p.layout_pages()
