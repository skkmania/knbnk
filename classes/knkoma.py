# -*- coding: utf-8 -*-
import logging
import pprint
import os
import numpy as np
import cv2
import os.path
import knparam as kr
import knpage as kp
import knutil as ku

__all__ = ["KnKoma", "KnKomaException", "KnKomaParamsException"]


class KnKomaException(Exception):
    def __init__(self, value):
        if value is None:
            self.initException()
        else:
            self.value = value

    def __str__(self):
        return repr(self.value)

    def printException(self):
        print "KnKoma Exception."

    @classmethod
    def paramsFileNotFound(self, value):
        print '%s not found.' % value

    @classmethod
    def initException(self):
        print "parameter file name must be specified."


class KnKomaParamsException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class KnKoma:

    def __init__(self, param=None):
        if param is None:
            raise KnKomaException('param must be specified.')
        else:
            if isinstance(param, kr.KnParam):
                self.p = param
                self.parameters = param['koma']
            else:
                raise KnKomaParamsException('param must be KnParam object')
            self.komaIdStr = self.p.get_komaIdStr()
            self.logger = logging.getLogger(param['param']['loggername'])
            self.logger.warning("KnKoma initialized :\n"
                                + pprint.pformat(self.p))
            self.komafp = '/'.join([param['param']['topdir'],
                          param['book']['bookdir'],
                          param['koma']['komadir']])
            self.imgfp = "/".join([self.komafp,
                                   self.p['koma']['imgfname']])
            self.get_img()
            self.im = ku.ImageManager(self)
            self.estimate_layouts()

    def __exit__(self, type, value, traceback):
        self.logger.debug('exit')

    @ku.deblog
    def start(self):
        self.get_page_img()
        self.mk_page_dirname()
        self.mk_page_param_dicts()
        self.mk_page_dir_and_write_img_file()
        for d in self.page_param_dicts:
            p = self.p.clone_for_page(d)
            kp.KnPage(p).start()

    @ku.deblog
    def mk_page_param_dicts(self):
        """
        pageをつくるKnParam obj をつくるためのparameter(dict obj)を用意する。
        副作用: self.page_param_dicts を設定する
        pageは複数個ありうるので、常にリストとして持つ

        """
        ret = [
            {
                "lr": "right",
                "pagedir": self.pagedirname['right'],
                "imgfname": self.p['koma']['komaIdStr'] + '_0.jpeg'},
            {
                "lr": "left",
                "pagedir": self.pagedirname['left'],
                "imgfname": self.p['koma']['komaIdStr'] + '_1.jpeg'}]
        self.logger.debug('mk_page_param_dict returns : %s' %
                          pprint.pformat(ret))
        self.page_param_dicts = ret
        return ret

    @ku.deblog
    def get_img(self):
        if os.path.exists(self.imgfp):
            self.img = cv2.imread(self.imgfp)
            if self.img is None:
                raise KnKomaException(self.imgfp + 'cannot be read')
            else:
                self.height, self.width, self.depth = self.img.shape
                self.centroids = []
                self.boxes = []
                self.candidates = {'upper': [], 'lower': [],
                                   'center': [], 'left': [], 'right': []}
        else:
            raise KnKomaException('%s not found' % self.imgfp)

    @ku.deblog
    def simply_divide_half(self):
        """
        画像の内容を考慮せず、外形的サイズのみから縦に半分にする
        副作用: self.leftPage, self.rightPage の設定
        """
        self.leftPage = self.img[:, :int(self.width / 2)]
        self.rightPage = self.img[:, int(self.width / 2):]

    @ku.deblog
    def estimate_layouts(self):
        """
        komaに何ページあるのか調べる
        副作用: self.numOfPages の設定
        [str of each page's style]
        """
        if 'info' in self.p:
            # まず外部からページ数などの情報が与えられているかcheck
            if 'numOfPages' in self.p['info']:
                self.numOfPages = self.p['info']['numOfPages']
                self.verify_given_info()
        else:
            self.set_pages_in_koma()
            self.make_pages_environment()

    @ku.deblog
    def set_pages_in_koma(self):
        """
        このコマに何ページあるのかを決定する
        副作用: self.pages_in_koma を設定する
        """
        if 'pages_in_koma' in self.p['book']:
            # book 全体にわたり決まっていて、所与ならばそれに従う
            self.pages_in_koma = self.p['book']['pages_in_koma']
        else:
            # 所与でないなら、画像により判断する
            self.pages_in_koma = self.im.find_pages_in_img()

    def verify_given_info(self):
        self.numOfPages = 2

    @ku.deblog
    def make_pages_environment(self):
        self.divide()
        self.mk_page_dirname()
        self.mk_page_param_dicts()
        self.mk_page_dir_and_write_img_file()

    @ku.deblog
    def divide(self):
        """
        self.imgを分割しleftPage, rightPageを生成する
        入力値: string : KnPage生成に必要なparameter file name
        戻り値: なし
        """
        self.cornerLines = self.im.get_corner_lines()
        self.originalCorner = self.im.get_original_corner()
        self.get_page_img()
        self.numOfPages = 2

    @ku.deblog
    def get_page_img(self):
        o = self.originalCorner
        self.leftPage = self.img[o['upper']:o['lower'],
                                 o['left']:o['center']]
        self.rightPage = self.img[o['upper']:o['lower'],
                                  o['center']:o['right']]

    @ku.deblog
    def mk_img_dirname(self):
        """
        """
        if self.im.complemented:
            ret = 'ss_%d' % self.parameters['scale_size']
            self.imgdirname = ret + '/complemented'
        else:
            ret = 'ss_%d' % self.parameters['scale_size']
            ret += '/can_%d_%d_%d' % tuple(self.parameters['canny'])
            ret += '/hgh_%d_%d_%d' % tuple(self.parameters['hough'])
            self.imgdirname = ret

    @ku.deblog
    def mk_page_dirname(self):
        """
        """
        if not hasattr(self, 'imgdirname'):
            self.mk_img_dirname()
        self.pagedirname = {
            'right': self.imgdirname + '/right',
            'left': self.imgdirname + '/left'
        }

    @ku.deblog
    def mk_page_dir_and_write_img_file(self):
        pagedir = '%s/%s' % (self.komafp, self.page_param_dicts[0]['pagedir'])
        if not os.path.exists(pagedir):
            os.makedirs(pagedir)
        self.right_page_fname = '/'.join(
            [pagedir, self.page_param_dicts[0]['imgfname']])
        cv2.imwrite(self.right_page_fname, self.rightPage)

        pagedir = '%s/%s' % (self.komafp, self.page_param_dicts[1]['pagedir'])
        if not os.path.exists(pagedir):
            os.makedirs(pagedir)
        self.left_page_fname = '/'.join(
            [pagedir, self.page_param_dicts[1]['imgfname']])
        cv2.imwrite(self.left_page_fname, self.leftPage)

    def update(self, v):
        self.val = v

    @ku.deblog
    def getContours(self, thresh_low=50, thresh_high=255):
        """
        contourの配列を返す
        """
        self.contours, self.hierarchy =\
            cv2.findContours(self.binarized,
                             cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    @ku.deblog
    def makeCandidates(self, umpire=None):
        if umpire is not None:
            pass
        else:
            for direction in ['upper', 'lower']:
                for line in self.horizLines:
                    if self.small_zone[direction][0] < line[0] <\
                            self.small_zone[direction][1]:
                        self.candidates[direction].append(line)
            for direction in ['center', 'right', 'left']:
                for line in self.vertLines:
                    if self.small_zone[direction][0] < line[0] <\
                            self.small_zone[direction][1]:
                        self.candidates[direction].append(line)

    @ku.deblog
    def writeContour(self):
        self.img_of_contours = np.zeros(self.img.shape, np.uint8)
        for point in self.contours:
            x, y = point[0][0]
            cv2.circle(self.img_of_contours, (x, y), 1, [0, 0, 255])

    @ku.deblog
    def write_data_file(self, outdir=None):
        """
        画像の統計データをテキストとして出力する
        """
        self.write_original_data_file()
        self.write_small_data_file()

    @ku.deblog
    def write_original_data_file(self, outdir=None):
        """
        original画像の統計データをテキストとして出力する
        """
        if not hasattr(self, 'contours'):
            self.getContours()
        if outdir is None:
            outdir = self.prepare_outdir()

        outfilename = ku.mkFilename(self, 'data', outdir)
        with open(outfilename, 'w') as f:
            f.write("contours\n")
            for cnt in self.contours:
                f.writelines(str(cnt))
                f.write("\n")

            f.write("\n\nhierarchy\n")
            for hic in self.hierarchy:
                f.writelines(str(hic))
                f.write("\n")

    @ku.deblog
    def write_small_data_file(self, outdir=None):
        """
        small画像の統計データをテキストとして出力する
        """
        if not hasattr(self, 'contours'):
            self.getContours()
        if outdir is None:
            outdir = self.prepare_outdir()

        outfilename = ku.mkFilename(self, 'data', outdir)
        with open(outfilename, 'w') as f:
            f.write("contours\n")
            for cnt in self.contours:
                f.writelines(str(cnt))
                f.write("\n")

            f.write("\n\nhierarchy\n")
            for hic in self.hierarchy:
                f.writelines(str(hic))
                f.write("\n")

    @ku.deblog
    def write_binarized_file(self, outdir=None):
        if not hasattr(self, 'contours'):
            self.getContours()
        if outdir is None:
            outdir = self.komafp
        outfilename = ku.mkFilename(self, '_binarized', outdir)
        cv2.imwrite(outfilename, self.binarized)

    @ku.deblog
    def write_small_img(self, outdir=None):
        if outdir is None:
            outdir = self.prepare_outdir()
        outfilename = ku.mkFilename(self, '_small_img', outdir)
        cv2.imwrite(outfilename, self.im.small_img)
        outfilename = ku.mkFilename(self, '_small_img_gray', outdir)
        cv2.imwrite(outfilename, self.im.small_img_gray)
        outfilename = ku.mkFilename(self, '_small_binarized', outdir)
        cv2.imwrite(outfilename, self.im.small_binarized)

    def prepare_outdir(self):
        if not hasattr(self, 'imgdirname'):
            self.mk_img_dirname()
        outdir = '%s/%s' % (self.komafp, self.imgdirname)
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        return outdir

    @ku.deblog
    def write_small_img_with_lines(self, outdir=None):
        if outdir is None:
            outdir = self.prepare_outdir()
        outfilename = ku.mkFilename(self, '_small_img_with_lines', outdir)
        if not hasattr(self.im, 'small_img_with_lines'):
            self.im.get_small_img_with_lines()
        cv2.imwrite(outfilename, self.im.small_img_with_lines)

    @ku.deblog
    def write_small_img_with_linesP(self, outdir=None):
        if outdir is None:
            outdir = self.prepare_outdir()
        outfilename = ku.mkFilename(self, '_small_img_with_linesP', outdir)
        if not hasattr(self.im, 'small_img_with_linesP'):
            self.im.get_small_img_with_linesP()
        cv2.imwrite(outfilename, self.im.small_img_with_linesP)

    @ku.deblog
    def include(self, box1, box2):
        """
           box1 が box2 を包含するならtrueを返す。
        """
        ax1, ay1, w1, h1 = box1
        ax2 = ax1 + w1
        ay2 = ay1 + h1
        bx1, by1, w2, h2 = box2
        bx2 = bx1 + w2
        by2 = by1 + h2

        if (ax1 <= bx1) and (bx2 <= ax2) and (ay1 <= by1) and (by2 <= ay2):
            return True
        else:
            return False

    @ku.deblog
    def get_boundingBox(self, boxes):
        """
        入力のboxの形式は(x,y,w,h)
        出力のboxの形式も(x,y,w,h)
        (x,y,w,h) -> (x,y,x+w,y+h)
        """
        target = [(x, y, x + w, y + h) for (x, y, w, h) in boxes]
        x1, y1, d1, d2 = map(min, zip(*target))
        d1, d2, x2, y2 = map(max, zip(*target))
        # (x,y,x+w,y+h) -> (x,y,x,y)
        return (x1, y1, x2 - x1, y2 - y1)
