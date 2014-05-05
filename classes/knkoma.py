# -*- coding: utf-8 -*-
import logging
import pprint
import os
import numpy as np
import itertools

import cv2
#import json
import os.path
#from operator import itemgetter, attrgetter
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
            self.komadir = '/'.join([param['param']['workdir'],
                           param['book']['bookdir'],
                           param['koma']['komadir']])
            self.workdir = self.p['koma']['komadir']
            if 'imgfullpath' in param['koma']:
                self.imgfname = param['koma']['imgfullpath']
            else:
                self.imgfname = "/".join([self.komadir,
                                          self.p['koma']['imgfname']])
            self.complemented = False
            self.get_img()

    def __exit__(self, type, value, traceback):
        self.logger.debug('exit')

    @ku.deblog
    def start(self):
        self.adjust_parameters()
        self.set_original_corner_lines()
        self.get_page_img()
        self.mk_page_dirname()
        self.mk_page_param_dicts()
        self.mk_page_dir_and_write_img_file()
        for d in self.page_param_dicts:
            p = self.p.clone_for_page(d)
            kp.KnPage(p).start()

    @ku.deblog
    def mk_page_param_dicts(self):
        ret = [
            {
                "lr": "right",
                "pagedir": self.pagedirname['right'],
                "imgfname": self.p['koma']['komaIdStr'] + '_0.jpeg'},
            {
                "lr": "left",
                "pagedir": self.pagedirname['left'],
                "imgfname": self.p['koma']['komaIdStr'] + '_1.jpeg'}]
        self.logger.debug('mk_page_param_dict returns : %s' % str(ret))
        self.page_param_dicts = ret
        return ret

    @ku.deblog
    def get_img(self):
        if os.path.exists(self.imgfname):
            self.img = cv2.imread(self.imgfname)
            if self.img is None:
                raise KnKomaException(self.imgfname + 'cannot be read')
            else:
                self.height, self.width, self.depth = self.img.shape
                self.centroids = []
                self.boxes = []
                self.candidates = {'upper': [], 'lower': [],
                                   'center': [], 'left': [], 'right': []}
                self.gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
                self.getBinarized()
        else:
            raise KnKomaException('%s not found' % self.imgfname)

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

        調査方法:

            まず外部からページ数などの情報が与えられているかcheck
            cornerLines を探して５本あれば２ページと判断する
        """
        if 'info' in self.p:
            if 'numOfPages' in self.p['info']:
                self.numOfPages = self.p['info']['numOfPages']

            self.verify_given_info()

        else:
            self.make_pages_environment()

    def verify_given_info(self):
        self.numOfPages = 2

    @ku.deblog
    def make_pages_environment(self):
        self.corner_finder = ku.CornerLineFinder(self)
        self.originalCorner = self.corner_finder.get_original_corner()
        self.get_page_img()
        self.mk_page_dirname()
        self.mk_page_param_dicts()
        self.mk_page_dir_and_write_img_file()
        self.numOfPages = 2

    @ku.deblog
    def divide(self, param=None):
        """
        self.imgを分割しleftPage, rightPageを生成する
        入力値: string : KnPage生成に必要なparameter file name
        戻り値: なし
        """
        self.cornerLines = {}
        try_count = 0
        while try_count < 5:
            self.prepareForLines()
            self.getHoughLines()
            if self.lines is None:
                self.logger.debug(
                    'lines not found. try count : %d' % try_count)
                self.changeparam(try_count)
                try_count += 1
                continue
            elif self.enoughLines():
                self.findCornerLines()
                if self.isCenterAmbiguous():
                    self.findCenterLine()
                # self.verifyCornerLines()
                break
            else:
                self.logger.debug(
                    'lines not enough. try count : %d' % try_count)
                self.changeparam(try_count)
                try_count += 1
        else:
            self.logger.debug('KnKoma#divide: retry over 5 times and gave up!')
            self.complement_corner_lines()

        self.set_original_corner_lines()
        self.get_page_img()

    @ku.deblog
    def get_page_img(self):
        o = self.originalCorner
        self.leftPage = self.img[o['upper']:o['lower'],
                                 o['left']:o['center']]
        self.rightPage = self.img[o['upper']:o['lower'],
                                  o['center']:o['right']]

    @ku.deblog
    def mk_page_dirname(self):
        self.pagedirname = {}
        if self.complemented:
            self.pagedirname = {}
            self.pagedirname['right'] = '/complemented/right'
            self.pagedirname['left'] = '/complemented/left'
        else:
            #ret = 'ss_%d' % self.scale_size
            ret = 'can_%d_%d_%d' % tuple(self.parameters['canny'])
            ret += '/hgh_%d_%d_%d' % tuple(self.parameters['hough'])
            self.pagedirname['right'] = ret + '/right'
            self.pagedirname['left'] = ret + '/left'

    @ku.deblog
    def mk_page_dir_and_write_img_file(self):
        pagedir = '%s/%s' % (self.komadir, self.page_param_dicts[0]['pagedir'])
        if not os.path.exists(pagedir):
            os.makedirs(pagedir)
        cv2.imwrite(self.page_param_dicts[0]['imgfname'],
                    self.rightPage)
        pagedir = '%s/%s' % (self.komadir, self.page_param_dicts[1]['pagedir'])
        if not os.path.exists(pagedir):
            os.makedirs(pagedir)
        cv2.imwrite(self.page_param_dicts[1]['imgfname'],
                    self.leftPage)

    def update(self, v):
        self.val = v

    @ku.deblog
    def getBinarized(self):
        """
        binarize された配列を self.binarized にセットする
        parameters必須。
        """
        if 'threshold' in self.parameters:
            thresh_low, thresh_high, typeval = self.parameters['threshold']
            ret, self.binarized =\
                cv2.threshold(self.gray, thresh_low, thresh_high, typeval)
            self.logger.debug('self.binarized created by threshold : %s',
                              str(self.parameters['threshold']))
        elif 'canny' in self.parameters:
            minval, maxval, apertureSize = self.parameters['canny']
            self.binarized = cv2.Canny(self.gray, minval, maxval, apertureSize)
            self.logger.debug('self.binarized created by canny : %s',
                              str(self.parameters['canny']))
        elif 'adaptive' in self.parameters:
            self.binarized =\
                cv2.adaptiveThreshold(self.gray,
                                      self.parameters['adaptive'])
            self.logger.debug('self.binarized created by adaptive : %s',
                              str(self.parameters['adaptive']))

    @ku.deblog
    def getContours(self, thresh_low=50, thresh_high=255):
        """
        contourの配列を返す
        """
        self.contours, self.hierarchy =\
            cv2.findContours(self.binarized,
                             cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    @ku.deblog
    def getHoughLinesP(self):
        self.linesP = cv2.HoughLinesP(self.small_img_canny,
                                      self.rho, self.theta, self.minimumVote)

    @ku.deblog
    def getLinePoints(self):
        """
        HoughLinesで取得するlines は
            [[rho, theta],...]
        と表現される。 それを
            [[(x1,y1), (x2,y2)],...]
        に変換する
        """
        self.linePoints = []
        for rho, theta in self.lines:
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho
            x1 = int(x0 + 1000 * (-b))
            y1 = int(y0 + 1000 * (a))
            x2 = int(x0 - 1000 * (-b))
            y2 = int(y0 - 1000 * (a))
            self.linePoints.append([(x1, y1), (x2, y2)])
        self.logger.debug('linePoints: # : %d' % len(self.linePoints))
        self.logger.debug('linePoints: %s' % str(self.linePoints))

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
    def write_lines_to_file(self, outdir):
        if not hasattr(self, 'lines'):
            self.getHoughLines()
            if self.lines is None:
                return False
        if not hasattr(self, 'linePoints'):
            self.getLinePoints()
        outfilename = ku.mkFilename(self, '_lines_data', outdir, ext='.txt')
        with open(outfilename, 'w') as f:
            f.write("stat\n")
            f.write("len of lines : " + str(len(self.lines)) + "\n")
            f.write("lines\n")
            f.write("[rho,  theta]\n")
            for line in self.lines:
                f.writelines(str(line))
                f.write("\n")
            f.write("\nlen of linePoints : "
                    + str(len(self.linePoints)) + "\n")
            f.write("linePoints\n")
            f.write("[(x1,y1), (x2,y2)]\n")
            for line in self.linePoints:
                f.writelines(str(line))
                f.write("\n")

    @ku.deblog
    def write_linesP_to_file(self, outdir):
        if not hasattr(self, 'linesP'):
            self.getHoughLinesP()
        outfilename = ku.mkFilename(self, '_linesP_data', outdir, ext='.txt')
        with open(outfilename, 'w') as f:
            f.write("stat\n")
            f.write("linesP\n")
            f.write("len of linesP[0] : " + str(len(self.linesP[0])) + "\n")
            f.write("\nlen of linesP: "
                    + str(len(self.linesP)) + "\n")
            f.write("[x1,y1,x2,y2]\n")
            for line in self.linesP:
                f.writelines(str(line))
                f.write("\n")

    @ku.deblog
    def writeContour(self):
        self.img_of_contours = np.zeros(self.img.shape, np.uint8)
        for point in self.contours:
            x, y = point[0][0]
            cv2.circle(self.img_of_contours, (x, y), 1, [0, 0, 255])

    @ku.deblog
    def get_small_img_with_lines(self):
        self.small_img_with_lines = self.small_img.copy()
        self.getLinePoints()
        for line in self.linePoints:
            cv2.line(self.small_img_with_lines,
                     line[0], line[1], (0, 0, 255), 2)

    @ku.deblog
    def get_small_img_with_linesP(self):
        self.small_img_with_linesP = self.small_img.copy()
        for line in self.linesP[0]:
            pt1 = tuple(line[:2])
            pt2 = tuple(line[-2:])
            cv2.line(self.small_img_with_linesP,
                     pt1, pt2, (0, 0, 255), 2)

    @ku.deblog
    def write_small_img(self, outdir=None):
        outfilename = ku.mkFilename(self, '_small_img', outdir)
        cv2.imwrite(outfilename, self.small_img)
        outfilename = ku.mkFilename(self, '_small_img_gray', outdir)
        cv2.imwrite(outfilename, self.small_img_gray)
        outfilename = ku.mkFilename(self, '_small_img_canny', outdir)
        cv2.imwrite(outfilename, self.small_img_canny)

    @ku.deblog
    def write_small_img_with_lines(self, outdir=None):
        outfilename = ku.mkFilename(self, '_small_img_with_lines', outdir)
        cv2.imwrite(outfilename, self.small_img_with_lines)

    @ku.deblog
    def write_small_img_with_linesP(self, outdir=None):
        outfilename = ku.mkFilename(self, '_small_img_with_linesP', outdir)
        cv2.imwrite(outfilename, self.small_img_with_linesP)

    @ku.deblog
    def write_data_file(self, outdir=None):
        if not hasattr(self, 'contours'):
            self.getContours()
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
        outfilename = ku.mkFilename(self, '_binarized', outdir)
        cv2.imwrite(outfilename, self.binarized)

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
