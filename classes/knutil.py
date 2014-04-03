# -*- coding: utf-8 -*-
import json
import os.path
import knpage as kp
import knkoma as kk

__all__ = ["read_params", "print_params_files", "check_test_environment",
           "mkFilename", "mkoutfilename",
           "KnUtilException", "KnUtilParamsException"]

DATA_DIR = '/home/skkmania/mnt2/workspace/pysrc/knbnk/data'


class KnUtilException(Exception):
    def __init__(self, value):
        if value is None:
            self.initException()
        else:
            self.value = value

    def __str__(self):
        return repr(self.value)

    def printException(self):
        print "KnUtil Exception."

    @classmethod
    def paramsFileNotFound(self, value):
        print '%s not found.' % value

    @classmethod
    def initException(self):
        print "parameter file name must be specified."


class KnUtilParamsException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def read_params(obj, params):
    with open(params) as f:
        lines = f.readlines()
    obj.parameters = json.loads(''.join(lines))
    try:
        if isinstance(obj, (kp.KnPage, kk.KnKoma)):
            obj.imgfname = obj.parameters['imgfname']
            obj.outfilename = obj.parameters['outfilename']
        obj.outdir = obj.parameters['outdir']
        obj.paramfname = obj.parameters['paramfname']
        obj.parameters['logfilename'] = obj.paramfname.replace('json', 'log')
    except KeyError as e:
        msg = 'key : %s must be in parameter file' % str(e)
        print msg
        raise KnUtilParamsException(msg)


def print_params_files(params_list):
    ret = []
    for params in params_list:
        fname = params['paramfname']
        with open(fname, 'w') as f:
            json.dump(params, f, sort_keys=False, indent=4)
            ret.append(fname)
    return ret


def check_test_environment(param_dict, bookId):
    """
    paramsに記述されたoutdirの存在確認
      なければ、tarballの展開とoutdirの作成
    parmsのtxt file( json format)の作成は常に行う
    (testのたびにそのtestの設定を使うこと。
    別のtestの影響を受けたくないので。)
    """
    if not os.path.exists(param_dict['outdir']):
        cmd = 'tar jxf %s/%s.tar.bz2 -C %s' % (DATA_DIR, bookId, DATA_DIR)
        os.system(cmd)
        cmd = "find %s -type d -name '*%s*' -exec mv {} %s \\;" %\
            (DATA_DIR, bookId, param_dict["outdir"])
        os.system(cmd)

    print_params_files([param_dict])


def mkFilename(obj, fix, outdir=None, ext=None):
    """
     fix : file name の末尾に付加する
     outdir : 出力先directoryの指定
     ext : 拡張子の指定 .txt のように、. ではじめる
    """
    dirname = os.path.dirname(obj.imgfname)
    basename = os.path.basename(obj.imgfname)
    if fix == 'data':
        name, ext = os.path.splitext(basename)
        if hasattr(obj, 'outfilename'):
            name = obj.outfilename
        name = name + '_data'
        ext = '.txt'
    else:
        if ext is None:
            name, ext = os.path.splitext(basename)
        else:
            name = os.path.splitext(basename)[0]

        if hasattr(obj, 'outfilename'):
            name = obj.outfilename
            if name == "auto":
                name = mkoutfilename(obj.parameters)
        name = name + fix

    if outdir is None:
        return os.path.join(dirname, name + ext)
    else:
        return os.path.join(outdir, name + ext)


def mkoutfilename(params, fix=None):
    res = 'o_' + os.path.basename(params['imgfname']).split('.')[0]
    keys = params.keys()
    if 'scale_size' in keys:
        res += "_ss_" + str(int(params['scale_size']))

    if 'hough' in keys:
        res += "_hgh_" + "_".join(map(str, params['hough']))

    if 'canny' in keys:
        res += "_can_" + "_".join(map(str, params['canny']))

    if 'sobel' in keys:
        res += "_sob_" + "_".join(map(str, params['sobel']))

    if 'scharr' in keys:
        res += "_sch_" + "_".join(map(str, params['scharr']))

    if fix:
        return res + fix
    else:
        return res
