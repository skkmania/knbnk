# -*- coding: utf-8 -*-
# params_file :  parameterをjson形式であらわしたテキストファイルboundingRectの大きさ指定
# params_file の書式 :  json text
#     注意：commaの有無
#      文字列のquotation 数字、配列以外は文字列なので""でくくること
#   {
#     以下は必須
#     "imgfname"     : "string"                 #  読み込む画像filename (full path)
#     "outdir"       : "string"                 #  出力するfileのdirectory
#     "paramfname"   : "string"                 # parameter file name
#                             (つまりこのfile自身のfull path)
#     以下は任意
#     "outfilename"  : "string",                # 出力するfileのbasenameを指定
#     "boundingRect" : [min, max],              # boundingRectの大きさ指定
#     "mode"         : findContoursのmode,      # EXTERNAL, LIST, CCOMP, TREE
#     "method"       : findContoursのmethod,    # NONE, SIMPLE, L1, KCOS

#   HoughLinesのparameter
#     "hough"        : [rho, theta, minimumVote]
#          rho : accuracy of rho.  integerを指定。1 など。
#          theta:  accuracy of theta. int(1 - 180)を指定。
#                  np.pi/180 などradianで考えるので、その分母を指定する。
#                  180なら1度ずつ、2なら水平と垂直の直線のみを候補とするという意味
#          minimumVote:
#          lineとみなすため必要な点の数。検出する線の長さに影響する。

#   以下の4つは排他。どれかひとつを指定。配列内の意味はopencvのdocを参照のこと
#     2値化のやりかたを決める重要な設定項目。
#     "canny"        : [threshold1, threshold2, apertureSize],
#     "threshold"    : [thresh, maxval, type],
#     "adaptive"     : [maxval, method, type, blockSize, C]
#     "harris"       : [blockSize, ksize, k]

#   以下の3つはgradientsのparameter。配列内の意味はopencvのdocを参照のこと
#     本プロジェクトには意味がない。
#     "scharr"       : [depth, dx, dy, scale, delta, borderType]
#     "sobel"        : [depth, dx, dy, ksize]
#     "laplacian"    : [depth]
#       これらのdepth は6 (=cv2.CV_64F)とするのが一般的
#
#   以下はpage_splitのparameter
# 処理するときの縦サイズ(px).
# 小さいほうが速いけど、小さすぎると小さい線が見つからなくなる.
#cvHoughLines2のパラメータもこれをベースに決める.
#     "scale_size"   : num  # 640.0 など対象画像の細かさに依存
# 最低オフセットが存在することを想定する(px).
# 真ん中にある謎の黒い線の上下をtop,bottomに選択しないためのテキトウな処理で使う.
#     "hard_offset"  : num  # 32
# ページ中心のズレの許容範囲(px / 2).
#  余白を切った矩形の中心からこの距離範囲の間でページの中心を決める.
#     "center_range" : num  # 64
# 中心を決める際に使う線の最大数.
#     "CENTER_SAMPLE_MAX" : num  # 1024
# 中心決めるときのクラスタ数
#     "CENTER_K" : num  # 3
#   }
#
#  5つのfileを生成する
#      出力0 :  statitics file  contourなどのデータのテキストファイル
#      出力1 :  findContourを適用する直前の画像のファイル
#      出力2 :  元の画像にcontourを重ね書きしたファイル
#      出力3 :  元の画像にcontourとそのboundingRectを重ね書きしたファイル
#      出力4 :  contourのみを書いたファイル
#      出力5 :  contourとそのboundingRectを重ね書きしたファイル

import sys
import numpy as np

import cv2
import json
import os.path
#from operator import itemgetter, attrgetter


class KnPageException(Exception):
    def __init__(self, value):
        if value is None:
            self.initException()
        else:
            self.value = value

    def __str__(self):
        return repr(self.value)

    def printException(self):
        print "KnPage Exception."

    @classmethod
    def paramsFileNotFound(self, value):
        print '%s not found.' % value

    @classmethod
    def initException(self):
        print "parameter file name must be specified."


class KnPageParamsException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class KnPage:

    def __init__(self, fname=None, datadir=None, params=None, outdir=None):
        if params is None:
            raise KnPageException('params is None')

        if os.path.exists(params):
            self.read_params(params)
            self.get_img()
        else:
            raise KnPageParamsException(params)
            # raise KnPageException.paramsFileNotFound(params)

    def read_params(self, params):
        with open(params) as f:
            lines = f.readlines()
        self.parameters = json.loads(''.join(lines))
        try:
            self.imgfname = self.parameters['imgfname']
            self.outdir = self.parameters['outdir']
            self.paramfname = self.parameters['paramfname']
        except KeyError as e:
            msg = 'key : %s must be in parameter file' % str(e)
            print msg
            raise KnPageParamsException(msg)
        self.outfilename = self.parameters['outfilename']

    def get_img(self):
        if os.path.exists(self.imgfname):
            self.img = cv2.imread(self.imgfname)
            if self.img is None:
                raise KnPageException(self.imgfname + 'cannot be read')
            else:
                self.height, self.width, self.depth = self.img.shape
                self.centroids = []
                self.boxes = []
                self.candidates = {'upper':[], 'lower':[], 'center':[], 'left':[], 'right':[]}
                self.gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
                self.getBinarized()
        else:
            raise KnPageException('%s not found' % self.imgfname)

    def divide(self):
        self.prepareForLines()
        self.getHoughLines()
        if self.enoughLines():
            self.findCornerLines()
            # self.verifyCornerLines()
        else:
            raise
        self.originalCorner = {}
        for d in ['upper', 'lower', 'center', 'right', 'left']:
            self.originalCorner[d] = int(self.cornerLines[d][0] / self.scale)

        oc = self.originalCorner
        self.leftPage = self.img[oc['upper']:oc['lower'], oc['left']:oc['center']]
        self.rightPage = self.img[oc['upper']:oc['lower'], oc['center']:oc['right']]

        self.write(self.mkFilename(fix='_left', ext='.jpeg'), self.leftPage)
        self.write(self.mkFilename(fix='_right', ext='.jpeg'), self.rightPage)

    def write(self, outfilename=None, om=None):
        if om is None:
            om = self.img
        #if hasattr(self, 'outfilename'):
        #    outfilename = self.outfilename
        #if outfilename:
        cv2.imwrite(outfilename, om)
        #else:
        #  raise

    def update(self, v):
        self.val = v

    def separate(self, arr, x):
        if x[1] - arr[-1][-1][1] < 15:
            arr[-1].append(x)
        else:
            arr.append([x])
        return arr

    def mkFilename(self, fix, outdir=None, ext=None):
        """
         fix : file name の末尾に付加する
         outdir : 出力先directoryの指定
         ext : 拡張子の指定 .txt のように、. ではじめる
        """
        dirname = os.path.dirname(self.imgfname)
        basename = os.path.basename(self.imgfname)
        if fix == 'data':
            name, ext = os.path.splitext(basename)
            if hasattr(self, 'outfilename'):
                name = self.outfilename
            name = name + '_data'
            ext = '.txt'
        else:
            if ext is None:
                name, ext = os.path.splitext(basename)
            else:
                name = os.path.splitext(basename)[0]

            if hasattr(self, 'outfilename'):
                name = self.outfilename
            name = name + fix

        if outdir is None:
            return os.path.join(dirname, name + ext)
        else:
            return os.path.join(outdir, name + ext)

    # サイズが box_min から box_max のbounding box の重心の配列を返す
    def getCentroids(self, box_min=16, box_max=48):
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
        if 'threshold' in self.parameters:
            thresh_low, thresh_high, typeval = self.parameters['threshold']
            ret, self.binarized =\
                cv2.threshold(self.gray, thresh_low, thresh_high, typeval)
        elif 'canny' in self.parameters:
            minval, maxval, apertureSize = self.parameters['canny']
            self.binarized = cv2.Canny(self.gray, minval, maxval, apertureSize)
        elif 'adaptive' in self.parameters:
            self.binarized =\
                cv2.adaptiveThreshold(self.gray,
                                      self.parameters['adaptive'])

    def getGradients(self):
        """
        self.img のgradients を self.gradients_* にセットする
        parameters必須。
        """
        if 'sobel' in self.parameters:
            ddepth, dx, dy, ksize = self.parameters['sobel']
            self.gradients_sobel = cv2.Sobel(self.gray, ddepth, dx, dy, ksize)
        if 'scharr' in self.parameters:
            ddepth, dx, dy = self.parameters['scharr']
            self.gradients_scharr = cv2.Scharr(self.gray, ddepth, dx, dy)
        if 'laplacian' in self.parameters:
            ddepth = self.parameters['laplacian'][0]
            self.gradients_laplacian = cv2.Laplacian(self.gray, ddepth)

    def getContours(self, thresh_low=50, thresh_high=255):
        """
        contourの配列を返す
        """
        self.contours, self.hierarchy =\
            cv2.findContours(self.binarized,
                             cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    def prepareForLines(self):
        if 'scale_size' in self.parameters:
            self.scale_size = self.parameters['scale_size']
            self.scale = self.scale_size / self.width
        else:
            raise KnPageParamsException('scale_size must be in param file')

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
        self.small_height, self.small_width, self.small_depth = self.small_img.shape
        self.small_img_gray = cv2.cvtColor(self.small_img, cv2.COLOR_BGR2GRAY)
        self.small_img_canny = cv2.Canny(self.small_img_gray,
                                         minval, maxval, apertureSize)
        self.rho = rho
        self.theta = theta
        self.minimumVote = minimumVote

    def getHoughLines(self):
        """
        戻り値: self.lines lineの配列
            この要素のlineは、(rho, theta). 2次元Hough space上の1点を指す
            OpenCVの戻り値は[[[0,1],[0,2],...,[]]]と外側に配列があるが、この関数の戻り値はそれをひとつ外して
            lineの配列としていることに注意。
            また、後々の処理の便宜のため、numpyのarrayからpythonのlistに変換し、
            theta, rhoの順に2段のkeyにもとづきsortしておく。
        """
        self.lines = cv2.HoughLines(self.small_img_canny,
                                    self.rho, self.theta, self.minimumVote)[0].tolist()
        self.lines.sort(key=lambda x: (x[1], x[0]))

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
                if max(line0[0][1], line0[1][1]) > max(line1[0][1], line1[1][1]):
                    return "upper"
                else:
                    return "lower"
            else:
                raise KnPageException('wrong recognition of line')
        else:
            if self.isVertical(line0) and self.isVertical(line1):
                if max(line0[0][0], line0[1][0]) > max(line1[0][0], line1[1][0]):
                    return "right"
                else:
                    return "left"
            else:
                raise KnPageException('wrong recognition of line')

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
        return len(self.candidates[direction]) > 0

    def makeSmallZone(self, levels=None):
        if levels is None:
            levels = { 'upper' : [0.03, 0.25],
                       'lower' : [0.75, 0.97],
                       'center': [0.45, 0.55],
                       'left'  : [0.03, 0.25],
                       'right' : [0.75, 0.97] }
        self.small_zone = {}
        for d in ['upper', 'lower']:
            self.small_zone[d] = [self.small_height * x for x in levels[d]]
        for d in ['center', 'left', 'right']:
            self.small_zone[d] = [self.small_width * x for x in levels[d]]

    def enoughLines(self):
        if len(self.lines) < 5:
            return False
        else:
            self.partitionLines()
            if len(self.horizLines) < 2 or len(self.vertLines) < 3:
                return False
            else:
                self.makeSmallZone()
                # self.makeCandidates()  # for debug
                for direction in ['upper', 'lower', 'center', 'right', 'left']:
                    if not self.lineSeemsToExist(direction):
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

#    def linesInZone(self, direction):
#        if direction in ['upper', 'lower']:
#            return [line for line
#                          in self.horizLines
#                             if self.small_zone[direction][0]
#                                 < line[0] <
#                                self.small_zone[direction][1]
#                   ]
#        else:
#            return [line for line in self.vertLines\
#                        if self.small_zone[direction][0] < line[0] <\
#                           self.small_zone[direction][1]]

    def findCornerLines(self):
        self.cornerLines = {}
        for (d, w) in [('upper', 'min'), ('lower', 'max'), ('center', 'center'),
                       ('left', 'min'), ('right', 'max')]:
            lines = self.candidates[d]
            if len(lines) == 0:
                raise
            elif len(lines) == 1:
                self.cornerLines[d] = lines[0]
            else:
                self.cornerLines[d] = self.selectLine(w, lines)

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
        if not hasattr(self, 'linePoints'):
            self.getLinePoints()
        outfilename = self.mkFilename('_lines_data', outdir, ext='.txt')
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
        outfilename = self.mkFilename('_linesP_data', outdir, ext='.txt')
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

    def write_gradients(self, outdir):
        for n in ['sobel', 'scharr', 'laplacian']:
            if n in self.parameters:
                outfilename = self.mkFilename('_' + n, outdir)
                img = getattr(self, 'gradients_' + n)
                cv2.imwrite(outfilename, img)

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

    def write_small_img(self, outdir):
        outfilename = self.mkFilename('_small_img', outdir)
        cv2.imwrite(outfilename, self.small_img)
        outfilename = self.mkFilename('_small_img_gray', outdir)
        cv2.imwrite(outfilename, self.small_img_gray)
        outfilename = self.mkFilename('_small_img_canny', outdir)
        cv2.imwrite(outfilename, self.small_img_canny)

    def write_small_img_with_lines(self, outdir):
        outfilename = self.mkFilename('_small_img_with_lines', outdir)
        cv2.imwrite(outfilename, self.small_img_with_lines)

    def write_small_img_with_linesP(self, outdir):
        outfilename = self.mkFilename('_small_img_with_linesP', outdir)
        cv2.imwrite(outfilename, self.small_img_with_linesP)

    def write_contours_bounding_rect_to_file(self, outdir=None):
        if not hasattr(self, 'contours'):
            self.getContours()
        om = np.zeros(self.img.shape, np.uint8)
        for cnt in self.contours:
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(om, (x, y), (x + w, y + h), [0, 255, 0])
            if (int(w) in range(60, 120)) or (int(h) in range(60, 120)):
                self.centroids.append((x + w / 2, y + h / 2))
                cv2.circle(om, (int(x + w / 2),
                                int(y + h / 2)), 5, [0, 255, 0])
        self.write(self.mkFilename('_cont_rect', outdir), om)

    def write_boxes_to_file(self, outdir):
        om = np.zeros(self.img.shape, np.uint8)
        for box in self.boxes:
            x, y, w, h = box
            cv2.rectangle(om, (x, y), (x + w, y + h), [0, 255, 0])
        self.write(self.mkFilename('_boxes', outdir), om)

    def write_data_file(self, outdir):
        if not hasattr(self, 'contours'):
            self.getContours()
        outfilename = self.mkFilename('data', outdir)
        with open(outfilename, 'w') as f:
            f.write("contours\n")
            for cnt in self.contours:
                f.writelines(str(cnt))
                f.write("\n")

            f.write("\n\nhierarchy\n")
            for hic in self.hierarchy:
                f.writelines(str(hic))
                f.write("\n")

    def write_binarized_file(self, outdir):
        if not hasattr(self, 'contours'):
            self.getContours()
        outfilename = self.mkFilename('_binarized', outdir)
        self.write(outfilename, self.binarized)

    def write_original_with_contour_file(self, outdir):
        if not hasattr(self, 'contours'):
            self.getContours()
        self.orig_w_cont = self.img.copy()
        for point in self.contours:
            x, y = point[0][0]
            cv2.circle(self.orig_w_cont, (x, y), 1, [0, 0, 255])
        outfilename = self.mkFilename('_orig_w_cont', outdir)
        self.write(outfilename, self.orig_w_cont)

    def write_original_with_contour_and_rect_file(self, outdir):
        if not hasattr(self, 'contours'):
            self.getContours()
        self.orig_w_cont_and_rect = self.img.copy()
        om = self.orig_w_cont_and_rect
        for cnt in self.contours:
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(om, (x, y), (x + w, y + h), [0, 255, 0])
            if (int(w) in range(60, 120)) or (int(h) in range(60, 120)):
                self.centroids.append((x + w / 2, y + h / 2))
                cv2.circle(om, (int(x + w / 2),
                                int(y + h / 2)), 5, [0, 255, 0])
            cx, cy = cnt[0][0]
            cv2.circle(om, (cx, cy), 2, [0, 0, 255])
        outfilename = self.mkFilename('_orig_w_cont_and_rect', outdir)
        self.write(outfilename, self.orig_w_cont_and_rect)

    def write_all(self, outdir):
        self.write_data_file(outdir)
        self.write_binarized_file(outdir)
        self.write_contours_bounding_rect_to_file(outdir)
        self.write_original_with_contour_file(outdir)
        self.write_original_with_contour_and_rect_file(outdir)
        self.write_collected_boxes_to_file(outdir)
        self.write_original_with_collected_boxes_to_file(outdir)

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

    def intersect(self, box1, box2, x_margin=20, y_margin=8):
        """
           box1 と box2 が交わるか接するならtrueを返す。
           marginを指定することですこし離れていても交わっていると判定させることができる
        """
        xm = x_margin
        ym = y_margin
        ax1, ay1, w1, h1 = box1
        ax2 = ax1 + w1
        ay2 = ay1 + h1
        bx1, by1, w2, h2 = box2
        bx2 = bx1 + w2
        by2 = by1 + h2

        if (bx1 in range(ax1 - xm, ax2 + xm)) and\
           (by1 in range(ay1 - ym, ay2 + ym)):
            return True
        if (bx2 in range(ax1 - xm, ax2 + xm)) and\
           (by2 in range(ay1 - ym, ay2 + ym)):
            return True
        if (bx2 in range(ax1 - xm, ax2 + xm)) and\
           (by1 in range(ay1 - ym, ay2 + ym)):
            return True
        if (bx1 in range(ax1 - xm, ax2 + xm)) and\
           (by2 in range(ay1 - ym, ay2 + ym)):
            return True
        if (ax1 in range(bx1 - xm, bx2 + xm)) and\
           (ay1 in range(by1 - ym, by2 + ym)):
            return True
        if (ax2 in range(bx1 - xm, bx2 + xm)) and\
           (ay2 in range(by1 - ym, by2 + ym)):
            return True
        if (ax2 in range(bx1 - xm, bx2 + xm)) and\
           (ay1 in range(by1 - ym, by2 + ym)):
            return True
        if (ax1 in range(bx1 - xm, bx2 + xm)) and\
           (ay2 in range(by1 - ym, by2 + ym)):
            return True

        return False

    def get_boundingBox(self, boxes):
        # 入力のboxの形式は(x,y,w,h)
        # 出力のboxの形式も(x,y,w,h)
        # (x,y,w,h) -> (x,y,x+w,y+h)
        target = [(x, y, x + w, y + h) for (x, y, w, h) in boxes]
        x1, y1, d1, d2 = map(min, zip(*target))
        d1, d2, x2, y2 = map(max, zip(*target))
        # (x,y,x+w,y+h) -> (x,y,x,y)
        return (x1, y1, x2 - x1, y2 - y1)

    def sweep_included_boxes(self, boxes=None):
        # 他のboxに完全に包含されるboxをリストから排除する
        flag = False
        if boxes is None:
            self.getContours()
            if len(self.boxes) == 0:
                self.getCentroids()
            boxes = self.boxes
            flag = True

      # w, h どちらかが200以上のboxは排除
        boxes = [x for x in boxes if (x[2] < 200) and (x[3] < 200)]

        temp_boxes = []
        while len(boxes) > 0:
            abox = boxes.pop()
            boxes = [x for x in boxes if not self.include(abox, x)]
            temp_boxes = [x for x in temp_boxes if not self.include(abox, x)]
            temp_boxes.append(abox)

        if flag:
            self.boxes = temp_boxes
        return temp_boxes

    def flatten(self, i):
        return reduce(
            lambda a, b: a + (self.flatten(b) if hasattr(b, '__iter__')
                              else [b]),
            i, [])

    def show_message(f):
        def wrapper():
            print("function called")
            return f()
        return wrapper

    def get_adj_boxes(self, boxes, abox):
        if abox in boxes:
            boxes.remove(abox)

        if len(abox) > 0:
            ret = [x for x in boxes if self.intersect(abox, x)]
        else:
            return []

        if len(ret) > 0:
            for x in ret:
                boxes.remove(x)
            if len(boxes) > 0:
                for x in ret:
                    subs = self.get_adj_boxes(boxes, x)
                    ret += subs
            else:
                return ret
            return ret
        else:
            return []

    def write_self_boxes_to_file(self, outdir):
        with open(self.mkFilename('_self_boxes', outdir, '.txt'), 'w') as f:
            f.write("self.boxes\n")
            for box in self.boxes:
                f.write(str(box) + "\n")
            f.write("\n")

    def collect_boxes(self):
        """
        bounding boxを包含するboxに統合し、文字を囲むboxの取得を試みる
        """

        if len(self.boxes) == 0:
            self.getCentroids()

        # w, h どちらかが200以上のboxは排除
        self.boxes = [x for x in self.boxes if (x[2] < 200) and (x[3] < 200)]

        outdir = '/home/skkmania/mnt2/workspace/pysrc/knbnk/data'
        self.write_self_boxes_to_file(outdir)    # for debug

        self.collected_boxes = []
        adjs = []

        f = open('while_process.txt', 'w')    # for debug
        while len(self.boxes) > 0:
            # for debug
            f.write('len of self.boxes : ' + str(len(self.boxes)) + "\n")
            abox = self.boxes.pop()
            f.write('abox : ' + str(abox) + "\n")    # for debug
            adjs = self.get_adj_boxes(self.boxes, abox)
            f.write('adjs : ' + str(adjs) + "\n")    # for debug
            for x in adjs:
                if x in self.boxes:
                    self.boxes.remove(x)
            f.write('len of self.boxes after remove : '
                    + str(len(self.boxes)) + "\n")    # for debug
            f.write('self.boxes after remove: '
                    + str(self.boxes) + "\n")    # for debug
            adjs.append(abox)
            f.write('adjs after append: ' + str(adjs) + "\n")    # for debug
            if len(adjs) > 0:
                boundingBox = self.get_boundingBox(adjs)
                f.write('boundingBox : '
                        + str(boundingBox) + "\n")    # for debug
                self.collected_boxes.append(boundingBox)
                f.write('self.collected_boxes : '
                        + str(self.collected_boxes) + "\n")    # for debug

        f.close()    # for debug

    def write_collected_boxes_to_file(self, outdir=None):
        if not hasattr(self, 'collected_boxes'):
            self.collect_boxes()

        om = np.zeros(self.img.shape, np.uint8)
        for box in self.collected_boxes:
            x, y, w, h = box
            cv2.rectangle(om, (x, y), (x + w, y + h), [0, 0, 255])
        self.write(self.mkFilename('_collected_box', outdir), om)

    def write_original_with_collected_boxes_to_file(self, outdir=None):
        if not hasattr(self, 'collected_boxes'):
            self.collect_boxes()
            self.boxes = self.collected_boxes
            self.collect_boxes()
            self.boxes = self.collected_boxes
            self.collect_boxes()

        self.orig_w_collected = self.img.copy()
        om = self.orig_w_collected
        for box in self.collected_boxes:
            x, y, w, h = box
            cv2.rectangle(om, (x, y), (x + w, y + h), [0, 0, 255])
        self.write(self.mkFilename('_orig_w_collected_box', outdir), om)

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
