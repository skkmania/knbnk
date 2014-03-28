# -*- coding: utf-8 -*-
import sys
import numpy as np
import cv2
import json
import os.path

__all__ = ["mkFilename"]


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

