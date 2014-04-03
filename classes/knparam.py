# -*- coding: utf-8 -*-
import logging
import os.path
import json
import knutil as ku
#import knkoma as kk
__all__ = ["KnParam", "KnParamException", "KnParamParamsException"]

MandatoryFields = ["paramfdir", "workdir", "outdir", "bookId",
                   "logfilename"]


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


class KnParam(dict):
    def __init__(self, param_dict=None, param_fname=None):
        dict.__init__(self)
        if param_dict:
            if isinstance(param_dict, dict):
                for k in param_dict:
                    self[k] = param_dict[k]
            else:
                raise KnParamParamsException('param_dict must be dict object.')
        elif param_fname:
            if isinstance(param_fname, str):
                if os.path.exists(param_fname):
                    with open(param_fname) as f:
                        lines = f.readlines()
                        j = json.loads(''.join(lines))
                    for k in j:
                        self[k] = j[k]
                else:
                    raise KnParamParamsException(param_fname + ' not found.')
            else:
                raise KnParamParamsException('param_fname must be string.')
        else:
            raise KnParamParamsException(
                'param_dict or param_fname must be specified.')

        for k in MandatoryFields:
            if not k in self.keys():
                raise KnParamParamsException(k)

        logging.basicConfig(filename=self['logfilename'])
        self.logger = logging.getLogger(self['bookId'])
        self.logger.warning(str(self))

    def isBook(self):
        """
        KnBookのparameterとしての必要条件を満たすか判定
        """
        if not "book" in self.keys():
            return False
        elif not "id" in self['book'].keys():
            return False
        else:
            return True

    def datadir(self):
        """
        出力: text : tarballが存在するdirectoryのfull path
        """
        return self['datadir']

    def paramfdir(self):
        """
        出力: text : parameter json fileが存在するdirectoryのfull path
        """
        return self['paramfdir']

    def workdir(self):
        """
        出力: text : tarballを展開し作成されるdirectoryのfull path
        """
        return self['workdir']

    def outdir(self):
        """
        出力: text : 最終成果物を出力する先のdirectoryのfull path
        """
        return self['outdir']

    def bookId(self):
        """
        出力: text : NDLの永続的識別子からとった数字の列
        """
        return self['bookId']

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
        ku.print_params_files([params])
        return params['paramfname']

    def check_params(self):
        for k in MandatoryFields:
            if not k in self.raw.keys():
                raise KnParamParamsException(k)

    def mkKomaParam(self, komanum):
        komanumstr = str(komanum).zfill(3)
        params = {}
        params['komanumstr'] = komanumstr
        params['paramfname'] = self.raw['outdir']\
            + '/k_' + komanumstr + '.json'
        params['imgfname'] = self.raw['outdir'] + '/'\
            + komanumstr + '.jpeg'
        params['outdir'] = self.raw['outdir']
        params['outfilename'] = "auto"
        params['mode'] = "EXTERNAL"
        params['method'] = "NONE"
        params['hough'] = [1, 2, 100]
        params['canny'] = [50, 200, 3]
        params['scale_size'] = 640.0
        ku.print_params_files([params])
        return params['paramfname']
