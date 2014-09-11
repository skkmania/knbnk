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
import pprint
import knkoma as kk
import knparam as kr
import knutil as ku
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
        self.bookfp = "/".join([param['param']['topdir'],
                                param['book']['bookdir']])
        self.logger = logging.getLogger(param['param']['loggername'])
        self.logger.warning("KnBook initialized :\n" + pprint.pformat(self.p))
        self.expand()
        self.read_metadata()
        self.check_komanum()

    @ku.deblog
    def start(self):
        self.logger.debug('# of koma in this book: %s', str(self.komanum))
        for k in range(1, self.komanum + 1):
            self.set_environment_for_a_koma(k)
            koma = kk.KnKoma(self.make_parameter_for_a_koma(k))
            koma.start()

    @ku.deblog
    def generate_a_koma(self, kid):
        """
        book内のコマのうち、kidで指定した番号のコマを生成する
          コマのdirectory を作成する。
          KnKoma objectを作成するためのparameter を作成する
          KnKoma objectを作成する

        戻り値： 作成した KnKoma object
        """
        self.set_environment_for_a_koma(kid)
        p = self.make_parameter_for_a_koma(kid)
        return kk.KnKoma(p)

    @ku.deblog
    def set_environment_for_a_koma(self, idx):
        """
        idxで指定したコマの
        directoryを作成
        そこに画像ファイルを移動する
        
        戻り値： 移動した画像のフルパス文字列
        """	
        komaIdStr = str(idx).zfill(3)
        workdir_for_koma = "/".join([self.bookfp, 'k' + komaIdStr])
        if not os.path.exists(workdir_for_koma):
            os.mkdir(workdir_for_koma)
        imgfname = self.bookfp + '/' + komaIdStr + self.ext

        if not os.path.exists(workdir_for_koma + '/' + komaIdStr + self.ext):
            shutil.move(imgfname, workdir_for_koma)
        return workdir_for_koma + '/' + komaIdStr + self.ext

    @ku.deblog
    def make_parameter_for_a_koma(self, idx):
        komaIdStr = str(idx).zfill(3)
        p = self.p.clone_for_koma({
            'komadir': 'k' + komaIdStr,
            'komaId': idx,
            'komaIdStr': komaIdStr,
            'imgfname':  komaIdStr + self.ext
        })
        ret = kr.KnParam(p)
        ret.set_logger(name=komaIdStr, logfilename=self.bookfp
                       + '/k' + komaIdStr + '/test.log')
        return ret

    @ku.deblog
    def expand(self):
        """
        tarballを展開する
        """
        if os.path.exists(self.arcdir + '/tmp'):
            os.system('rm -fr "%s"' % self.arcdir + '/tmp')
        else:
            os.mkdir(self.arcdir + '/tmp')

        if not os.path.exists(self.bookfp):
            cmd = 'tar jxf %s/%s.tar.bz2 -C %s/tmp' % (
                self.arcdir, self.bookId, self.arcdir)
            self.logger.debug('cmd: %s', cmd)
            os.system(cmd)
            cmd = "find %s/tmp/* -type d -name 'original' -exec mv {} %s \\;"\
                % (self.arcdir, self.bookfp)
            self.logger.debug('cmd: %s', cmd)
            os.system(cmd)
            cmd = "find %s/tmp/* -type f -name '*.json' -exec mv {} %s \\;" %\
                (self.arcdir, self.bookfp)
            self.logger.debug('cmd: %s', cmd)
            os.system(cmd)
            cmd = "find %s/tmp -type d -name '*%s*' -exec mv {} %s \\;" %\
                (self.arcdir, self.bookId, self.bookfp)
            self.logger.debug('cmd: %s', cmd)
            os.system(cmd)

        if os.path.exists(self.bookfp + '/001.jpeg'):
            self.ext = '.jpeg'
        elif os.path.exists(self.bookfp + '/001.jpg'):
            self.ext = '.jpg'
        else:
            raise 'KnBook#expand: image file 001 not found'

    @ku.deblog
    def read_metadata(self):
        self.metafname = '%s/common_%s.json' % (self.bookfp, self.bookId)
        if os.path.exists(self.metafname):
            with open(self.metafname) as f:
                lines = f.readlines()
                self.metadata = json.loads(''.join(lines))
                self.komanum = int(self.metadata['lastContentNo'])
        else:
            raise KnBookException('metadata file "%s" not found.'
                                  % self.metafname)

    @ku.deblog
    def check_komanum(self):
        """
        metadataで読んだlastContentNo と
        展開した画像ファイルの数が一致するかチェック
        一致しなければlogに警告を記載しておく.
        画像のあるidx だけを集めたリストをself.koma_indicies として保持する
        """
        self.koma_indicies = range(1, self.komanum + 1)
        for idx in self.koma_indicies:
            filename = '%s/%s%s' % (self.bookfp, str(idx).zfill(3), self.ext)
            if not os.path.exists(filename):
                self.logger.warning('!!! image file %s.%s not found!!!' %
                                    (str(idx), self.ext))
                self.koma_indicies.remove(idx)

    @ku.deblog
    def divide_all(self):
        """
        book内の全コマをdivideする
        全コマのObjectをself.komasに保存する。
        (なので、コマ数が少ないときだけ実行すること。)
        """
        for k in range(1, self.komanum + 1):
            self.p.set_komaId(current=k)
            koma = kk.KnKoma(param=self.p)
            koma.divide()

    @ku.deblog
    def collect_all(self):
        for k in self.komas:
            for p in k.pages:
                p.collect_boxes()

    @ku.deblog
    def layout_all(self):
        for k in self.komas:
            for p in k.pages:
                p.layout_pages()
