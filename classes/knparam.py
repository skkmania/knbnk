# -*- coding: utf-8 -*-
import logging
import copy
import os.path
import json
import knutil as ku
import knbook as kb
#import knkoma as kk
__all__ = ["KnParam", "KnParamException", "KnParamParamsException"]

MandatoryFields = {
    "param": ["arcdir", "paramfdir", "workdir", "outdir",
              "paramfname", "logfilename", "balls"],
    "book":  ["bookdir", "bookId"],
    "koma":  ["komadir", "komaId", "komaIdStr",
              "scale_size", "hough", "canny", "imgfname"],
    "page":  ["pagedir", "imgfname", "lr", "boundingRect",
              "mode", "method"]
}


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
        if param_dict is None and param_fname is None:
            raise KnParamParamsException(
                'param_dict or param_fname must be specified.')
        elif param_dict:
            if isinstance(param_dict, dict):
                for k in param_dict:
                    self[k] = param_dict[k]
            else:
                raise KnParamParamsException('param_dict must be dict object.')
        else:
            if isinstance(param_fname, str):
                self.read_paramf(param_fname)
            else:
                raise KnParamParamsException('param_fname must be string.')

        self.mandatory_check()

        logging.basicConfig(filename=self['param']['logfilename'],
                            level=logging.DEBUG,
                            format='%(asctime)s %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p')
        self.logger = logging.getLogger(self['book']['bookId'])
        self.logger.warning(str(self))

    def read_paramf(self, param_fname):
        if os.path.exists(param_fname):
            with open(param_fname) as f:
                lines = f.readlines()
                j = json.loads(''.join(lines))
            for k in j:
                self[k] = j[k]
        else:
            raise KnParamParamsException(param_fname + ' not found.')

    def mandatory_check(self):
        for k, v in MandatoryFields.items():
            if not k in self.keys():
                raise KnParamParamsException(k)
            else:
                for f in v:
                    if not f in self[k].keys():
                        raise KnParamParamsException(f)

    def clone(self):
        tmp = {}
        for k in self:
            tmp[k] = copy.deepcopy(self[k])
        return KnParam(tmp)

    def start(self):
        self.check_environment()
        self.expand_tarballs()

    def check_environment(self):
        pass

    def expand_tarballs(self):
        for ball in self.ball_list():
            self.logger.debug(ball)
            p = self.clone_for_book(ball)
            kb.KnBook(p).start()

    def ball_list(self):
        return self['param']["balls"]

    def clone_for_book(self, ball):
        """
        自らをKnBookに渡すに当たって、対象のtarballやbookIdをトップレベルにもってくるなど
        自らの中身を調整する
        """
        ret = self.clone()
        ret['book']["bookdir"] = self['param']['workdir'] + '/' + ball
        ret['book']["bookId"] = ball
        return ret

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
        return self['param']['datadir']

    def paramfdir(self):
        """
        出力: text : parameter json fileが存在するdirectoryのfull path
        """
        return self['param']['paramfdir']

    def workdir(self):
        """
        出力: text : tarballを展開し作成されるdirectoryのfull path
        """
        return self['param']['workdir']

    def outdir(self):
        """
        出力: text : 最終成果物を出力する先のdirectoryのfull path
        """
        return self['param']['outdir']

    def bookId(self):
        """
        出力: text : NDLの永続的識別子からとった数字の列
        """
        return self['book']['bookId']

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
        if komanum < 1000:
            komanumstr = str(komanum).zfill(3)
        else:
            komanumstr = str(komanum).zfill(4)
        params = {}
        params['komanumstr'] = komanumstr
        params['paramfname'] = self['param']['outdir']\
            + '/k_' + komanumstr + '.json'
        params['imgfname'] = self['param']['outdir'] + '/'\
            + komanumstr + '.jpeg'
        params['outdir'] = self['param']['outdir']
        params['outfilename'] = "auto"
        params['mode'] = "EXTERNAL"
        params['method'] = "NONE"
        params['hough'] = [1, 2, 100]
        params['canny'] = [50, 200, 3]
        params['scale_size'] = 640.0
        ku.print_params_files([params])
        return params['param']['paramfname']

    def get_numOfKoma(self):
        return self['book']['numOfKoma']

    def set_numOfKoma(self, n):
        self['book']['numOfKoma'] = n

    def get_komaIdStr(self):
        return self['koma']['komaIdStr']

    def set_komaId(self, current, last):
        if last < 1000:
            komaIdStr = str(current).zfill(3)
        else:
            komaIdStr = str(current).zfill(4)
        self['koma']['komaIdStr'] = komaIdStr
        self['koma']['komaId'] = current
        return komaIdStr

    def get_imgfname(self):
        if 'imgfname' in self['koma']:
            return self['koma']['imgfname']
        else:
            return self['koma']['imgfname']

    def set_imgfname(self, current, last):
        if last < 1000:
            komaIdStr = str(current).zfill(3)
        else:
            komaIdStr = str(current).zfill(4)
        self['koma']['imgfname'] = "/".join(
            [self['param']['workdir'], 'k' + komaIdStr, komaIdStr + ".jpeg"])

    def set_lr(self, lr):
        self['page']['lr'] = lr

    def lrstr(self):
        return self['page']['lr']

    def clone_for_page(self, page):
        ret = self.clone()
        ret['page'].update(page)
        return ret

    def clone_for_koma(self, koma):
        ret = self.clone()
        ret['koma'].update(koma)
        return ret
