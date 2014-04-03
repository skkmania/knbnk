# -*- coding: utf-8 -*-
import os.path
import json
#import knkoma as kk
__all__ = ["KnParam", "KnParamException", "KnParamParamsException"]

MandatoryFields = ["paramfdir", "workdir", "outdir", "bookId"]


class KnParamException(Exception):
    def __init__(self, value):
        if value is None:
            self.initException()
        else:
            self.value = value

    def __str__(self):
        return repr(self.value)

    def printException(self):
        print "KnParam Exception."

    @classmethod
    def paramsFileNotFound(self, value):
        print '%s not found.' % value

    @classmethod
    def initException(self):
        print "parameter file name must be specified."


class KnParamParamsException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        if self.value in MandatoryFields:
            return repr("param file lacks %s." % self.value)
        else:
            return repr(self.value)


class KnParam:
    def __init__(self, param=None, param_fname=None):
        if param is None and param_fname is None:
            raise KnParamException('must specify fname or params')

        if os.path.exists(param_fname):
            with open(param_fname) as f:
                lines = f.readlines()
            self.raw = json.loads(''.join(lines))
        else:
            raise KnParamParamsException(param_fname)

        self.check_params()

    def datadir(self):
        """
        出力: text : tarballが存在するdirectoryのfull path
        """
        return self.raw['datadir']

    def paramfdir(self):
        """
        出力: text : parameter json fileが存在するdirectoryのfull path
        """
        return self.raw['paramfdir']

    def workdir(self):
        """
        出力: text : tarballを展開し作成されるdirectoryのfull path
        """
        return self.raw['workdir']

    def outdir(self):
        """
        出力: text : 最終成果物を出力する先のdirectoryのfull path
        """
        return self.raw['outdir']

    def bookId(self):
        """
        出力: text : NDLの永続的識別子からとった数字の列
        """
        return self.raw['bookId']

    def mkPageParam(self, komanum):
        komanumstr = str(komanum).zfill(3)
        params = {}
        params['komanumstr'] = komanumstr
        params['paramfname'] = self.parameters['outdir']\
            + '/k_' + komanumstr + '.json'
        params['imgfname'] = self.parameters['outdir'] + '/'\
            + komanumstr + '.jpeg'
        params['outdir'] = self.parameters['outdir']
        params['outfilename'] = "auto"
        params['mode'] = "EXTERNAL"
        params['method'] = "NONE"
        params['hough'] = [1, 2, 100]
        params['canny'] = [50, 200, 3]
        params['scale_size'] = 640.0
        print_params_files([params])
        return params['paramfname']

    def check_params(self):
        for k in MandatoryFields:
            if not k in self.raw.keys():
                raise KnParamParamsException(k)

    def mkKomaParam(self, komanum):
        komanumstr = str(komanum).zfill(3)
        params = {}
        params['komanumstr'] = komanumstr
        params['paramfname'] = self.parameters['outdir']\
            + '/k_' + komanumstr + '.json'
        params['imgfname'] = self.parameters['outdir'] + '/'\
            + komanumstr + '.jpeg'
        params['outdir'] = self.parameters['outdir']
        params['outfilename'] = "auto"
        params['mode'] = "EXTERNAL"
        params['method'] = "NONE"
        params['hough'] = [1, 2, 100]
        params['canny'] = [50, 200, 3]
        params['scale_size'] = 640.0
        print_params_files([params])
        return params['paramfname']
