# -*- coding: utf-8 -*-
import logging
import os
import sys
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
            self.logger = logging.getLogger(self.komaIdStr)
            self.workdir = self.p['koma']['komadir']
            self.imgfname = "/".join([self.p['koma']['komadir'],
                                      self.p['koma']['imgfname']])
            self.complemented = False
            self.get_img()

    def __exit__(self, type, value, traceback):
        self.logger.debug('exit')

    def start(self):
        self.logger.debug('KnKoma started')
        self.adjust_parameters()
        self.set_original_corner_lines()
        self.get_page_img()
        self.mk_page_dirname()
        self.mk_page_param_dicts()
        self.mk_page_dir_and_write_img_file()
        for d in self.page_param_dicts:
            p = self.p.clone_for_page(d)
            kp.KnPage(p).start()

    def mk_page_param_dicts(self):
        pd0 = self.workdir + '/' + self.pagedirname['right']
        pd1 = self.workdir + '/' + self.pagedirname['left']
        ret = [
            {
                "lr": "right",
                "pagedir": pd0,
                "imgfname": pd0 +
                '/' + self.p['koma']['komaIdStr'] + '_0.jpeg'},
            {
                "lr": "left",
                "pagedir": pd1,
                "imgfname": pd1 +
                '/' + self.p['koma']['komaIdStr'] + '_1.jpeg'}]
        self.logger.debug('mk_page_param_dict returns : %s' % str(ret))
        self.page_param_dicts = ret
        return ret

    def get_img(self):
        self.logger.debug('entered in get_img')
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
                self.logger.debug('successfully leaving from get_img.')
        else:
            raise KnKomaException('%s not found' % self.imgfname)

    def changeparam(self, cnt):
        rho, theta, minimumVote = self.parameters['hough']
        minimumVote = int(0.9 * minimumVote)
        self.parameters['hough'] = [rho, theta, minimumVote]

        minval, maxval, apertureSize = self.parameters['canny']
        maxval = int(0.9 * maxval)
        self.parameters['canny'] = [minval, maxval, apertureSize]
        self.logger.debug('hough : %s' % str(self.parameters['hough']))
        self.logger.debug('canny : %s' % str(self.parameters['canny']))

    def simply_divide_half(self):
        self.leftPage = self.img[:, :int(self.width / 2)]
        self.rightPage = self.img[:, int(self.width / 2):]
        self.write_page_img_to_file()

    def isCenterAmbiguous(self):
        return len(self.candidates['left']) > 0 and\
            len(self.candidates['center']) > 0 and\
            len(self.candidates['right']) > 0

    def estimate_layouts(self):
        """
        komaに何ページあるのか調べる
        副作用: self.layouts の設定
        [str of each page's style]
        """
        self.layouts = ["graph", "graph"]

    def adjust_parameters(self):
        """
        self.imgを分割しleftPage, rightPageを生成する
        その過程でparameterを調整する
        戻り値：なし
        """
        self.logger.debug('entered in adjust_parameters')
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

    def divide(self, param=None):
        """
        self.imgを分割しleftPage, rightPageを生成する
        入力値: string : KnPage生成に必要なparameter file name
        戻り値: なし
        """
        self.logger.debug('entered in divide')
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
        self.write_page_img_to_file()

    def set_original_corner_lines(self):
        self.originalCorner = {}
        for d in ['upper', 'lower', 'center', 'right', 'left']:
            self.originalCorner[d] = int(self.cornerLines[d][0] / self.scale)

    def get_page_img(self):
        o = self.originalCorner
        self.leftPage = self.img[o['upper']:o['lower'],
                                 o['left']:o['center']]
        self.rightPage = self.img[o['upper']:o['lower'],
                                  o['center']:o['right']]

    def mk_page_dirname(self):
        self.pagedirname = {}
        if self.complemented:
            self.pagedirname = {}
            self.pagedirname['right'] = '/complemented/right'
            self.pagedirname['left'] = '/complemented/left'
        else:
            ret = 'ss_%d' % self.scale_size
            ret += '/can_%d_%d_%d' % tuple(self.parameters['canny'])
            ret += '/hgh_%d_%d_%d' % tuple(self.parameters['hough'])
            self.pagedirname['right'] = ret + '/right'
            self.pagedirname['left'] = ret + '/left'

    def mk_page_dir_and_write_img_file(self):
        pagedir = self.page_param_dicts[0]['pagedir']
        if not os.path.exists(pagedir):
            os.makedirs(pagedir)
        cv2.imwrite(self.page_param_dicts[0]['imgfname'],
                    self.rightPage)
        pagedir = self.page_param_dicts[1]['pagedir']
        if not os.path.exists(pagedir):
            os.makedirs(pagedir)
        cv2.imwrite(self.page_param_dicts[1]['imgfname'],
                    self.leftPage)

    def update(self, v):
        self.val = v

    def separate(self, arr, x):
        if x[1] - arr[-1][-1][1] < 15:
            arr[-1].append(x)
        else:
            arr.append([x])
        return arr

    def getCentroids(self, box_min=16, box_max=48):
        """
        サイズが box_min から box_max のbounding box の重心の配列を返す
        """
        if not hasattr(self, 'contours'):
            self.getContours()

        if hasattr(self, 'parameters'):
            # if self.parameters.has_key('boundingRect'):
            if 'boundingRect' in self.parameters:
                box_min, box_max = self.parameters['boundingRect']

        for cnt in self.contours:
            box = cv2.boundingRect(cnt)
            self.boxes.append(box)
            x, y, w, h = box
            if (int(w) in range(box_min, box_max)) or\
               (int(h) in range(box_min, box_max)):
                self.centroids.append((x + w / 2, y + h / 2))

    def getBinarized(self):
        """
        binarize された配列を self.binarized にセットする
        parameters必須。
        """
        self.logger.debug('enterd in getBinarized')
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

    def getContours(self, thresh_low=50, thresh_high=255):
        """
        contourの配列を返す
        """
        self.contours, self.hierarchy =\
            cv2.findContours(self.binarized,
                             cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    def prepareForLines(self):
        """
        縮小画像を作成
        hough parameters (rho, theta, minimumVote)をいったん確定しておく
        canny parameters (minval, maxval, apertureSize)をいったん確定しておく
        """
        if 'scale_size' in self.parameters:
            self.scale_size = self.parameters['scale_size']
            self.scale = self.scale_size / self.width
        else:
            raise KnKomaParamsException('scale_size must be in param file')

        if 'hough' in self.parameters:
            rho, theta, minimumVote = self.parameters['hough']
            theta = np.pi / theta
        else:
            rho, theta, minimumVote = [1, np.pi / 180, 120]

        if 'canny' in self.parameters:
            minval, maxval, apertureSize = self.parameters['canny']
        else:
            minval, maxval, apertureSize = [50, 200, 3]

        self.small_img = cv2.resize(self.img,
                                    (int(self.width * self.scale),
                                     int(self.height * self.scale)))
        self.small_height, self.small_width, self.small_depth =\
            self.small_img.shape
        self.small_img_gray = cv2.cvtColor(self.small_img, cv2.COLOR_BGR2GRAY)
        self.small_img_canny = cv2.Canny(self.small_img_gray,
                                         minval, maxval, apertureSize)
        self.rho = rho
        self.theta = theta
        self.minimumVote = minimumVote

    def getHoughLines(self):
        """
        small_img_canny からHough lineを算出しておく
        戻り値: self.lines lineの配列
            この要素のlineは、(rho, theta). 2次元Hough space上の1点を指す
            OpenCVの戻り値は[[[0,1],[0,2],...,[]]]と外側に配列があるが、
            この関数の戻り値はそれをひとつ外して
            lineの配列としていることに注意。
            また、後々の処理の便宜のため、numpyのarrayからpythonのlistに変換し、
            theta, rhoの順に2段のkeyにもとづきsortしておく。
        """
        tmplines = cv2.HoughLines(self.small_img_canny,
                                  self.rho, self.theta,
                                  self.minimumVote)
        if tmplines is not None:
            self.lines = tmplines[0].tolist()
            self.lines.sort(key=lambda x: (x[1], x[0]))
        else:
            self.lines = None

    def getHoughLinesP(self):
        self.linesP = cv2.HoughLinesP(self.small_img_canny,
                                      self.rho, self.theta, self.minimumVote)

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

    def compLine(self, line0, line1, horv):
        """
        line0, line1 の形式は2点指定式。[(x0,y0), (x1,y1)]
        line0, line1 の関係を返す
        horv :  "h" or "v" を指定
        """
        if horv == 'h':
            if self.isHorizontal(line0) and self.isHorizontal(line1):
                if max(line0[0][1], line0[1][1]) >\
                        max(line1[0][1], line1[1][1]):
                    return "upper"
                else:
                    return "lower"
            else:
                raise KnKomaException('wrong recognition of line')
        else:
            if self.isVertical(line0) and self.isVertical(line1):
                if max(line0[0][0], line0[1][0]) >\
                        max(line1[0][0], line1[1][0]):
                    return "right"
                else:
                    return "left"
            else:
                raise KnKomaException('wrong recognition of line')

    def partitionLines(self):
        self.horizLines = filter(self.isHorizontal, self.lines)
        self.vertLines = filter(self.isVertical, self.lines)

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

    def lineSeemsToExist(self, direction, umpire=None):
        if umpire is not None:
            pass
        else:
            if direction in ['upper', 'lower']:
                for line in self.horizLines:
                    if self.small_zone[direction][0] < line[0] <\
                            self.small_zone[direction][1]:
                        self.candidates[direction].append(line)
            else:
                for line in self.vertLines:
                    if self.small_zone[direction][0] < line[0] <\
                            self.small_zone[direction][1]:
                        self.candidates[direction].append(line)
        self.logger.debug('direction : %s' % direction)
        self.logger.debug('candidates: %s' % str(self.candidates[direction]))
        return len(self.candidates[direction]) > 0

    def makeSmallZone(self, levels=None):
        """
        cornerLinesは経験上画像の4辺から、この程度離れたところに存在している
        はずだという数値
        HoughLinesを取得したあと、cornerLinesを絞りこむために利用する。
        """
        if levels is None:
            levels = {'upper':  [0.03, 0.1],
                      'lower':  [0.9, 0.97],
                      'center': [0.45, 0.55],
                      'left':   [0.03, 0.1],
                      'right':  [0.9, 0.97]}
        self.small_zone = {}
        for d in ['upper', 'lower']:
            self.small_zone[d] = [self.small_height * x for x in levels[d]]
        for d in ['center', 'left', 'right']:
            self.small_zone[d] = [self.small_width * x for x in levels[d]]

    def enoughLines(self):
        komanumstr = self.p['koma']['komaIdStr']
        self.logger.info('# of self.lines in %s : %s' %
                         (komanumstr, len(self.lines)))
        if len(self.lines) < 5:
            self.logger.debug('self.lines : %s' % str(self.lines))
            self.logger.debug('enoughLines returns *False*' +
                              ' because this poor Lines')
            return False
        else:
            self.partitionLines()
            if len(self.horizLines) < 2 or len(self.vertLines) < 3:
                self.logger.debug(
                    'self.horizLines : %s' % str(self.horizLines))
                self.logger.debug('self.vertLines : %s' % str(self.vertLines))
                self.logger.debug('enoughLines returns *False*' +
                                  ' because this poor (horiz|vert)Lines')
                return False
            else:
                self.makeSmallZone()
                # self.makeCandidates()  # for debug
                for d in ['upper', 'lower', 'center', 'right', 'left']:
                    if not self.lineSeemsToExist(d):
                        self.logger.debug('enoughLines returns *False*' +
                                          ' because %s has 0 candidates' % d)
                        return False
        return True

    def selectLine(self, way, lines):
        if way == 'center':
            lines.sort(key=lambda x: abs((self.small_width / 2) - x[0]))
            return lines[0]
        else:
            lines.sort(key=lambda x: x[0])
            if way == 'min':
                return lines[0]
            elif way == 'max':
                return lines[-1]

    def findCenterLine(self):
        self.logger.debug('entered in findCenterLine:')
        self.logger.debug(str(self.cornerLines))
        self.logger.debug(str(self.candidates))
        diffOfPageWidth = lambda (left, center, right):\
            abs((right[0] - center[0]) - (center[0] - left[0]))
        tuplesOfVertLines =\
            sorted(itertools.product(self.candidates['left'],
                                     self.candidates['center'],
                                     self.candidates['right']),
                   key=diffOfPageWidth)
        self.cornerLines['center'] = tuplesOfVertLines[0][1]
        self.logger.debug('just before exitting findCenterLine:')
        self.logger.debug(str(self.cornerLines))

    def findCornerLines(self):
        self.logger.debug('entered in findCornerLines:')
        self.logger.debug(str(self.cornerLines))
        for (d, w) in [('upper', 'min'), ('lower', 'max'),
                       ('left', 'min'), ('right', 'max')]:
            lines = self.candidates[d]
            if len(lines) == 0:
                pass
            elif len(lines) == 1:
                self.cornerLines[d] = lines[0]
            else:
                self.cornerLines[d] = self.selectLine(w, lines)
        self.logger.debug('just before exitting findCornerLines:')
        self.logger.debug(str(self.cornerLines))

    def complement_corner_lines(self):
        half_pi = 1.5707963705062866
        self.logger.debug('entered in complement_corner_lines:')
        self.logger.debug(str(self.cornerLines))
        self.findCornerLines()
        for d in ['upper', 'lower', 'left', 'right']:
            if (not (d in self.candidates)) or (len(self.candidates[d]) == 0):
                if d == 'upper':
                    self.cornerLines[d] = [
                        int(self.small_height * 0.15), half_pi]
                elif d == 'lower':
                    self.cornerLines[d] = [
                        int(self.small_height * 0.9), half_pi]
                elif d == 'left':
                    self.cornerLines[d] = [int(self.small_width * 0.1), 0]
                elif d == 'right':
                    self.cornerLines[d] = [int(self.small_width * 0.9), 0]
        self.cornerLines['center'] = [int(self.small_width * 0.5), 0]
        self.logger.debug('just before exitting complement_corner_lines:')
        self.logger.debug(str(self.cornerLines))
        self.complemented = True

    def findCornerLineP(self):
        a = self.linePoints
        vlines = [vline for vline in a if abs(vline[0][0] - vline[1][0]) < 50]
        hlines = [hline for hline in a if abs(hline[0][1] - hline[1][1]) < 50]
        upper_hline = hlines[0]
        lower_hline = hlines[0]
        for line in hlines:
            if self.compLine(line, upper_hline, 'h') == "upper":
                upper_hline = line

            if self.compLine(line, lower_hline, 'h') == "lower":
                lower_hline = line

        right_vline = vlines[0]
        left_vline = vlines[0]
        for line in vlines:
            if self.compLine(line, right_vline, 'v') == "right":
                right_vline = line

            if self.compLine(line, left_vline, 'v') == "left":
                left_vline = line

    def findCenterLineP(self):
        pass

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

    def writeContour(self):
        self.img_of_contours = np.zeros(self.img.shape, np.uint8)
        for point in self.contours:
            x, y = point[0][0]
            cv2.circle(self.img_of_contours, (x, y), 1, [0, 0, 255])

    def get_small_img_with_lines(self):
        self.small_img_with_lines = self.small_img.copy()
        self.getLinePoints()
        for line in self.linePoints:
            cv2.line(self.small_img_with_lines,
                     line[0], line[1], (0, 0, 255), 2)

    def get_small_img_with_linesP(self):
        self.small_img_with_linesP = self.small_img.copy()
        for line in self.linesP[0]:
            pt1 = tuple(line[:2])
            pt2 = tuple(line[-2:])
            cv2.line(self.small_img_with_linesP,
                     pt1, pt2, (0, 0, 255), 2)

    def write_small_img(self, outdir=None):
        outfilename = ku.mkFilename(self, '_small_img', outdir)
        cv2.imwrite(outfilename, self.small_img)
        outfilename = ku.mkFilename(self, '_small_img_gray', outdir)
        cv2.imwrite(outfilename, self.small_img_gray)
        outfilename = ku.mkFilename(self, '_small_img_canny', outdir)
        cv2.imwrite(outfilename, self.small_img_canny)

    def write_small_img_with_lines(self, outdir=None):
        outfilename = ku.mkFilename(self, '_small_img_with_lines', outdir)
        cv2.imwrite(outfilename, self.small_img_with_lines)

    def write_small_img_with_linesP(self, outdir=None):
        outfilename = ku.mkFilename(self, '_small_img_with_linesP', outdir)
        cv2.imwrite(outfilename, self.small_img_with_linesP)

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

    def write_binarized_file(self, outdir=None):
        if not hasattr(self, 'contours'):
            self.getContours()
        outfilename = ku.mkFilename(self, '_binarized', outdir)
        cv2.imwrite(outfilename, self.binarized)

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

    def show_message(f):
        def wrapper():
            print("function called")
            return f()
        return wrapper

    def isVertical(self, line):
        """
         line = [[x1, y1],[x2, y2]]
         line = (rho, theta)
         を判別して対応
        """
        if isinstance(line[0], list) or isinstance(line[0], tuple):
            return (line[0][0] == line[1][0])
        else:
            return line[1] < 0.01

    def isHorizontal(self, line):
        """
         line = [[x1, y1],[x2, y2]]
         line = (rho, theta)
         を判別して対応
        """
        if isinstance(line[0], list) or isinstance(line[0], tuple):
            return (line[0][1] == line[1][1])
        else:
            return abs(line[1] - np.pi / 2) < 0.01

    def getIntersection(self, line1, line2):
        """
         Finds the intersection of two lines, or returns false.
         line1 = [[x1, y1],[x2, y2]]
         line2 = [[x1, y1],[x2, y2]]
        """
        s1 = np.array([float(x) for x in line1[0]])
        e1 = np.array([float(x) for x in line1[1]])

        s2 = np.array([float(x) for x in line2[0]])
        e2 = np.array([float(x) for x in line2[1]])

        if self.isVertical(line1):
            if self.isVertical(line2):
                return False
            else:
                a2 = (s2[1] - e2[1]) / (s2[0] - e2[0])
                b2 = s2[1] - (a2 * s2[0])
                x = line1[0][0]
                y = a2 * x + b2

        elif self.isVertical(line2):
            a1 = (s1[1] - e1[1]) / (s1[0] - e1[0])
            b1 = s1[1] - (a1 * s1[0])
            x = line2[0][0]
            y = a1 * x + b1

        elif self.isHorizontal(line1):
            if self.isHorizontal(line2):
                return False
            else:
                a2 = (s2[1] - e2[1]) / (s2[0] - e2[0])
                b2 = s2[1] - (a2 * s2[0])
                y = line1[0][1]
                x = (y - b2) / a2

        elif self.isHorizontal(line2):
            a1 = (s1[1] - e1[1]) / (s1[0] - e1[0])
            b1 = s1[1] - (a1 * s1[0])
            y = line1[1][1]
            x = (y - b1) / a1

        else:
            a1 = (s1[1] - e1[1]) / (s1[0] - e1[0])
            b1 = s1[1] - (a1 * s1[0])
            a2 = (s2[1] - e2[1]) / (s2[0] - e2[0])
            b2 = s2[1] - (a2 * s2[0])

            if abs(a1 - a2) < sys.float_info.epsilon:
                return False

            x = (b2 - b1) / (a1 - a2)
            y = a1 * x + b1

        return (int(round(x)), int(round(y)))
