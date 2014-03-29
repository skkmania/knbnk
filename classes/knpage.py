# -*- coding: utf-8 -*-
import numpy as np
import cv2
import json
import os.path
#from operator import itemgetter, attrgetter
from .knutil import *


__all__ = ['KnPage', 'KnPageException', 'KnPageParamsException']


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
        self.parameters = dict(json.loads(''.join(lines)))
        try:
            self.imgfname = self.parameters['imgfname']
            self.outdir = self.parameters['outdir']
            self.paramfname = self.parameters['paramfname']
        except KeyError as e:
            msg = 'key : %s must be in parameter file' % str(e)
            print msg
            raise KnPageParamsException(msg)
        if 'outfilename' in self.parameters:
            self.outfilename = self.parameters['outfilename']
            if self.outfilename == "auto":
                self.outfilename = mkoutfilename(self.parameters)
        else:
            self.outfilename = mkoutfilename(self.parameters)

    def get_img(self):
        if os.path.exists(self.imgfname):
            self.img = cv2.imread(self.imgfname)
            if self.img is None:
                raise KnPageException(self.imgfname + 'cannot be read')
            else:
                self.height, self.width, self.depth = self.img.shape
                self.centroids = []
                self.boxes = []
                self.candidates = {'upper': [], 'lower': [],
                                   'center': [], 'left': [], 'right': []}
                self.gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
                self.getBinarized()
        else:
            raise KnPageException('%s not found' % self.imgfname)

    def write(self, outfilename=None, om=None):
        if om is None:
            om = self.img
        if outfilename is None:
            if hasattr(self, 'outfilename'):
                outfilename = self.outfilename
            else:
                raise
        cv2.imwrite(outfilename, om)

    def update(self, v):
        self.val = v

    def separate(self, arr, x):
        if x[1] - arr[-1][-1][1] < 15:
            arr[-1].append(x)
        else:
            arr.append([x])
        return arr

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

    def writeContour(self):
        self.img_of_contours = np.zeros(self.img.shape, np.uint8)
        for point in self.contours:
            x, y = point[0][0]
            cv2.circle(self.img_of_contours, (x, y), 1, [0, 0, 255])

    def write_gradients(self, outdir=None):
        for n in ['sobel', 'scharr', 'laplacian']:
            if n in self.parameters:
                if not 'outfilename' in self.parameters:
                    outfilename = mkFilename(self, '_' + n,
                                             outdir=outdir, ext='.jpeg')
                else:
                    outfilename = self.parameters['outfilename']
                if outfilename == "auto":
                    outfilename = mkFilename(self, '_' + n,
                                             outdir=outdir, ext='.jpeg')
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
        outfilename = mkFilename(self, '_small_img', outdir)
        cv2.imwrite(outfilename, self.small_img)
        outfilename = mkFilename(self, '_small_img_gray', outdir)
        cv2.imwrite(outfilename, self.small_img_gray)
        outfilename = mkFilename(self, '_small_img_canny', outdir)
        cv2.imwrite(outfilename, self.small_img_canny)

    def write_small_img_with_lines(self, outdir):
        outfilename = mkFilename(self, '_small_img_with_lines', outdir)
        cv2.imwrite(outfilename, self.small_img_with_lines)

    def write_small_img_with_linesP(self, outdir):
        outfilename = mkFilename(self, '_small_img_with_linesP', outdir)
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
        self.write(mkFilename(self, '_cont_rect', outdir), om)

    def write_boxes_to_file(self, outdir):
        om = np.zeros(self.img.shape, np.uint8)
        for box in self.boxes:
            x, y, w, h = box
            cv2.rectangle(om, (x, y), (x + w, y + h), [0, 255, 0])
        self.write(mkFilename(self, '_boxes', outdir), om)

    def write_data_file(self, outdir):
        if not hasattr(self, 'contours'):
            self.getContours()
        outfilename = mkFilename(self, 'data', outdir)
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
        outfilename = mkFilename(self, '_binarized', outdir)
        self.write(outfilename, self.binarized)

    def write_original_with_contour_file(self, outdir=None):
        if not hasattr(self, 'contours'):
            self.getContours()
        self.orig_w_cont = self.img.copy()
        for point in self.contours:
            x, y = point[0][0]
            cv2.circle(self.orig_w_cont, (x, y), 1, [0, 0, 255])
        outfilename = mkFilename(self, '_orig_w_cont', outdir)
        self.write(outfilename, self.orig_w_cont)

    def write_original_with_contour_and_rect_file(self, outdir=None):
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
        outfilename = mkFilename(self, '_orig_w_cont_and_rect', outdir)
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

    def sweep_included_boxes(self, boxes=None):
        """
        他のboxに完全に包含されるboxをリストから排除する
        """
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
        """
        隣接するboxのリストを返す
        入力：
        boxes : boxのリスト。探索対象。
        abox : あるbox。探索の起点。このboxに隣接するboxからなるリストを返す。
        ここで隣接するとは、直接aboxに隣接するもの,
                            間接的にaboxに隣接するもの(隣の隣もそのまた隣もみな隣とみなす。)
        をどちらも含める。
        それゆえ、linked listを再帰でたどるのと同様に、この関数も再帰を利用している。
        出力: boxのリスト
        """
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
        with open(mkFilename(self, '_self_boxes', outdir, '.txt'), 'w') as f:
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
        self.write(mkFilename(self, '_collected_box', outdir), om)

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
        self.write(mkFilename(self, '_orig_w_collected_box', outdir), om)

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
