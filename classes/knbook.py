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
import logging
import knkoma as kk
import knparam as kr
#import knutil as ku
import shutil
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
    def __init__(self, param):
        if param is None:
            raise KnBookException('param must be given.')

        if isinstance(param, kr.KnParam):
            self.p = param
        else:
            raise KnBookParamsException('param must be a KnParam object.')
        self.arcdir = param['param']['arcdir']
        self.bookId = param['book']['bookId']
        self.bookdir = param['book']['bookdir']
        self.logger = logging.getLogger('knbook')
        self.expand()
        self.read_metadata()

    def start(self):
        self.logger.debug('KnBook started')
        self.expand()
        self.read_metadata()
        self.logger.debug('komanum: %s', str(self.komanum))
        for k in range(1, self.komanum + 1):
            komaIdStr = self.p.set_komaId(current=k, last=self.komanum + 1)
            self.p.set_imgfname(current=k, last=self.komanum + 1)
            imgfname = self.set_environment_for_koma(komaIdStr)
            p = self.p.clone_for_koma({
                'komadir': self.bookdir + '/k' + komaIdStr,
                'komaId': k,
                'komaIdStr': komaIdStr,
                'imgfname':  imgfname
            })
            koma = kk.KnKoma(p)
            koma.start()

    def set_environment_for_koma(self, komaIdStr):
        workdir_for_koma = "/".join([self.bookdir, 'k' + komaIdStr])
        if not os.path.exists(workdir_for_koma):
            os.mkdir(workdir_for_koma)
        imgfname = self.bookdir + '/' + komaIdStr + self.ext
        shutil.move(imgfname, workdir_for_koma)
        return workdir_for_koma + '/' + komaIdStr + self.ext

    def expand(self):
        self.logger.debug('enterd into KnBook#expand')
        if os.path.exists(self.arcdir + '/tmp'):
            os.system('rm -fr "%s"' % self.arcdir + '/tmp')
        else:
            os.mkdir(self.arcdir + '/tmp')
        if not os.path.exists(self.bookdir):
            cmd = 'tar jxf %s/%s.tar.bz2 -C %s/tmp' % (
                self.arcdir, self.bookId, self.arcdir)
            self.logger.debug('cmd: %s', cmd)
            os.system(cmd)
            cmd = "find %s/tmp/* -type d -name 'original' -exec mv {} %s \\;"\
                % (self.arcdir, self.bookdir)
            self.logger.debug('cmd: %s', cmd)
            os.system(cmd)
            cmd = "find %s/tmp/* -type f -name '*.json' -exec mv {} %s \\;" %\
                (self.arcdir, self.bookdir)
            self.logger.debug('cmd: %s', cmd)
            os.system(cmd)
            cmd = "find %s/tmp -type d -name '*%s*' -exec mv {} %s \\;" %\
                (self.arcdir, self.bookId, self.bookdir)
            self.logger.debug('cmd: %s', cmd)
            os.system(cmd)
        if os.path.exists(self.bookdir + '/001.jpeg'):
            self.ext = '.jpeg'
        elif os.path.exists(self.bookdir + '/001.jpg'):
            self.ext = '.jpg'
        else:
            raise 'KnBook#expand: image file 001 not found'

    def read_metadata(self):
        self.metafname = (self.p['book']['bookdir']
                          + '/common_' + self.p.bookId() + '.json')
        if os.path.exists(self.metafname):
            with open(self.metafname) as f:
                lines = f.readlines()
                self.metadata = json.loads(''.join(lines))
                self.komanum = int(self.metadata['lastContentNo'])
        else:
            raise KnBookException('metadata file "%s" not found.'
                                  % self.metafname)

    def divide_all(self):
        """
        book内の全コマをdivideする
        全コマのObjectをself.komasに保存する。
        (なので、コマ数が少ないときだけ実行すること。)
        """
        for k in range(1, self.komanum + 1):
            self.p.set_komanum(current=k, last=self.komanum + 1)
            koma = kk.KnKoma(param=self.p)
            koma.divide()

    def divide_a_koma(self, komanum):
        """
        book内のコマのうち、komanumで指定した番号のコマをdivideする
        コマのObjectは保存しない。
        戻り値：KnPage objectのtuple(leftPage, rightPage)
        """
        koma = kk.KnKoma(param=self.p, komanum=komanum)
        return koma.divide()

    def collect_all(self):
        for k in self.komas:
            for p in k.pages:
                p.collect_boxes()

    def layout_all(self):
        for k in self.komas:
            for p in k.pages:
                p.layout_pages()
