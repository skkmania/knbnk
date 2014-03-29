# -*- coding: utf-8 -*-
import sys
import numpy as np
import cv2
import json
import os.path

__all__ = ["print_params_files", "check_test_environment", "mkFilename", "mkoutfilename"]


def print_params_files(params_list):
    ret = []
    for params in params_list:
        fname = params['paramfname']
        with open(fname, 'w') as f:
            json.dump(params, f, sort_keys=False, indent=4)
            ret.append(fname)
    return ret


def check_test_environment(params, bookId):
    """
    paramsに記述されたoutdirの存在確認
      なければ、tarballの展開とoutdirの作成
    parmsのtxt file( json format)の作成は常に行う
    (testのたびにそのtestの設定を使うこと。
    別のtestの影響を受けたくないので。)
    """
    if not os.path.exists(params['outdir']):
        cmd = 'tar jxf %s/%s.tar.bz2 -C %s' % (DATA_DIR, bookId, DATA_DIR)
        os.system(cmd)
        cmd = "find %s -type d -name '*%s*' -exec mv {} %s \\;" %\
            (DATA_DIR, bookId, params["outdir"])
        os.system(cmd)

    print_params_files([params])


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
