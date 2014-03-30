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
import knpage as kp
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
    def __init__(self, fname=None, datadir=None, params=None, outdir=None):
        if params is None:
            raise KnBookException('params is None')

        if os.path.exists(params):
            read_params(self, params)
            self.expand()
            self.read_metadata()
        else:
            raise KnBookParamsException(params)
            # raise KnBookException.paramsFileNotFound(params)

    def expand(self):
        if not os.path.exists(self.parameters['outdir']):
            cmd = 'tar jxf %s/%s.tar.bz2 -C %s' % (
                DATA_DIR, self.parameter['bookId'], DATA_DIR)
            os.system(cmd)
            cmd = "find %s -type d -name '*%s*' -exec mv {} %s \\;" %\
                (DATA_DIR, self.parameter['bookId'], self.parameters["outdir"])
            os.system(cmd)

    def read_metadata(self):
        self.metafname = (self.parameters['outdir']
                          + '/raw_' + self.parameters['bookId'] + '.json')
        if os.path.exists(self.parameters['outdir']):
            with open(self.metafname) as f:
                lines = f.readlines()
                self.metadata = json.loads(''.join(lines))
                self.komanum = int(self.metadata['lastContentNo'])

    def divide_pages(self):
        for k in range(1, self.komanum + 1):
            koma = kk.KnKoma(params=self.mkKomaParam(k))
            koma.divide()

    def mkKomaParam(self, komanum):
        params = {}
        params['paramfname'] = self.parameters['outdir']\
            + '/k_' + str(komanum).zfill(3) + '.json'
        params['imgfname'] =  self.parameters['outdir'] + '/'\
            + str(komanum).zfill(3) + '.jpeg'
        params['outdir'] = self.parameters['outdir']
        params['outfilename'] = "auto"
        params['mode'] = "EXTERNAL"
        params['method'] = "NONE"
        params['hough'] = [1, 2, 100]
        params['canny'] = [50, 200, 3]
        params['scale_size'] = 640.0
        print_params_files([params])
        return params['paramfname']
