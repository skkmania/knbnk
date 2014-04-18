# -*- coding: utf-8 -*-
import numpy as np
import cv2
#import json
import os.path
import logging
from operator import itemgetter
from scipy import stats
import knutil as ku
import knparam as kr


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
    def __init__(self, param):
        if param is None:
            raise KnPageException('param must be specified.')
        else:
            if isinstance(param, kr.KnParam):
                self.read_parameter(param)
            else:
                raise KnPageParamsException('param must be KnParam object')
            self.get_img()
            self.lrstr = self.p.lrstr()
            self.logger = logging.getLogger(self.lrstr)
            self.collected_boxes = []

    def read_parameter(self, param):
        self.p = param
        self.parameters = param['page']
        if "mavstd" in self.parameters:
            self.mavstd = self.parameters['mavstd']
        else:
            self.mavstd = 10
        if "pgmgn" in self.parameters:
            self.pgmgn_x, self.pgmgn_y = self.parameters['pgmgn']
        else:
            self.pgmgn_x, self.pgmgn_y = [0.05, 0.05]
        # collectされたのに小さすぎるのはなにかの間違いとして排除
        #  mcbs : minimum collected box size
        if 'mcbs' in self.p['page']:
            self.mcbs = self.p['page']['mcbs']
        else:
            self.mcbs = 10

    def start(self):
        #self.getChars()
        #self.layoutChars()
        self.getBinarized()
        d = self.p['page']['pagedir']
        self.write_original_with_collected_boxes_to_file(d)
        pass

    def get_img(self):
        self.imgfname = "/".join([self.p['page']['pagedir'],
                                  self.p['page']['imgfname']])
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

    def update(self, v):
        self.val = v

    def separate(self, arr, x):
        if x[1] - arr[-1][-1][1] < 15:
            arr[-1].append(x)
        else:
            arr.append([x])
        return arr

    def getBoxesAndCentroids(self, box_min=16, box_max=48):
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
                    outfilename = ku.mkFilename(self, '_' + n,
                                                outdir=outdir, ext='.jpeg')
                else:
                    outfilename = self.parameters['outfilename']
                if outfilename == "auto":
                    outfilename = ku.mkFilename(self, '_' + n,
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
        outfilename = ku.mkFilename(self, '_small_img', outdir)
        cv2.imwrite(outfilename, self.small_img)
        outfilename = ku.mkFilename(self, '_small_img_gray', outdir)
        cv2.imwrite(outfilename, self.small_img_gray)
        outfilename = ku.mkFilename(self, '_small_img_canny', outdir)
        cv2.imwrite(outfilename, self.small_img_canny)

    def write_small_img_with_lines(self, outdir):
        outfilename = ku.mkFilename(self, '_small_img_with_lines', outdir)
        cv2.imwrite(outfilename, self.small_img_with_lines)

    def write_small_img_with_linesP(self, outdir):
        outfilename = ku.mkFilename(self, '_small_img_with_linesP', outdir)
        cv2.imwrite(outfilename, self.small_img_with_linesP)

    def write_contours_bounding_rect_to_file(self, outdir=None):
        self.logger.debug('enterd in write_contours_bounding_rect_to_file')
        if not hasattr(self, 'contours'):
            self.getContours()
        self.logger.debug('# of contours : %d' % len(self.contours))
        om = np.zeros(self.img.shape, np.uint8)
        for cnt in self.contours:
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(om, (x, y), (x + w, y + h), [0, 255, 0])
            if (int(w) in range(60, 120)) or (int(h) in range(60, 120)):
                self.centroids.append((x + w / 2, y + h / 2))
                cv2.circle(om, (int(x + w / 2),
                                int(y + h / 2)), 5, [0, 255, 0])
        cv2.imwrite(ku.mkFilename(self, '_cont_rect', outdir), om)

    def count_contours_bounding_rects(self):
        self.logger.debug('enterd in count_contours_bounding_rects')
        if not hasattr(self, 'contours'):
            self.getContours()
        self.logger.debug('# of contours : %d' % len(self.contours))
        for cnt in self.contours:
            x, y, w, h = cv2.boundingRect(cnt)

    def write_boxes_to_file(self, outdir=None, target=None, fix=None):
        if outdir is None:
            outdir = self.parameters['pagedir']
        if target is None:
            s, e = None, None
        else:
            s, e = target
        boxes = self.boxes[s:e]
        x_sorted_boxes = self.x_sorted_boxes[s:e]
        y_sorted_boxes = self.y_sorted_boxes[s:e]
        for t in [(boxes, '_boxes%s' % fix),
                  (x_sorted_boxes, '_x_sorted_boxes%s' % fix),
                  (y_sorted_boxes, '_y_sorted_boxes%s' % fix)]:
            om = np.zeros(self.img.shape, np.uint8)
            for box in t[0]:
                x, y, w, h = box
                cv2.rectangle(om, (x, y), (x + w, y + h), [0, 255, 0])
            cv2.imwrite(ku.mkFilename(self, t[1], outdir), om)

    def write_data_file(self, outdir):
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

    def write_original_with_contour_file(self, outdir=None):
        if not hasattr(self, 'contours'):
            self.getContours()
        self.orig_w_cont = self.img.copy()
        for point in self.contours:
            x, y = point[0][0]
            cv2.circle(self.orig_w_cont, (x, y), 1, [0, 0, 255])
        outfilename = ku.mkFilename(self, '_orig_w_cont', outdir)
        cv2.imwrite(outfilename, self.orig_w_cont)

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
        outfilename = ku.mkFilename(self, '_orig_w_cont_and_rect', outdir)
        cv2.imwrite(outfilename, self.orig_w_cont_and_rect)

    def write_all(self, outdir):
        """
        5つのfileを生成する
            出力0 :  statitics file  contourなどのデータのテキストファイル
            出力1 :  findContourを適用する直前の画像のファイル
            出力2 :  元の画像にcontourを重ね書きしたファイル
            出力3 :  元の画像にcontourとそのboundingRectを重ね書きしたファイル
            出力4 :  contourのみを書いたファイル
            出力5 :  contourとそのboundingRectを重ね書きしたファイル
        """
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
                self.getBoxesAndCentroids()
            boxes = self.boxes
            flag = True

        temp_boxes = []
        while len(boxes) > 0:
            abox = boxes.pop()
            boxes = [x for x in boxes if not self.include(abox, x)]
            temp_boxes = [x for x in temp_boxes if not self.include(abox, x)]
            temp_boxes.append(abox)

        if flag:
            self.boxes = temp_boxes
        return temp_boxes

    def sort_boxes(self):
        """
        x_sorted : xの昇順、yの昇順に並べる
        y_sorted : yの昇順、xの昇順に並べる
        """
        if not hasattr(self, 'boxes'):
            self.getContours()
            if len(self.boxes) == 0:
                self.getBoxesAndCentroids()

        self.x_sorted_boxes = sorted(self.boxes, key=itemgetter(0, 1))
        self.y_sorted_boxes = sorted(self.boxes, key=itemgetter(1, 0))

    def calc_box_distance(self):
        """
        sorted_boxesに、隣のboxとの距離情報を追加する
        [box1, box2, box3, box4] ->
          [(box1, d12), (box2, d23), (box3, d34), (box4, inf)]
          dij : tuple : distance between boxi and boxj : (dx, dy)
          inf : (10000, 10000) means infinity
        """
        #dist_x = [(x1 - x0)]

    def get_neighbors(self, box, x, y):
        """
        self.boxesから、boxの近所にあるboxを選びそのリストを返す
        近所とは、boxをx方向にx，y方向にy拡大した矩形と交わることとする
        """
        x0, y0, w, h = box
        x1 = max(0, x0 - x)
        y1 = max(0, y0 - y)
        w = w + 2 * x
        h = h + 2 * y
        newbox = (x1, y1, w, h)
        ret = [b for b in self.boxes if self.intersect(newbox, b, 0, 0)]
        if box in ret:
            ret.remove(box)
        return ret

    def sweep_maverick_boxes(self):
        """
        他のboxから離れて存在しているboxをself.boxesから排除する
        """
        boxes = self.boxes
        for box in boxes:
            neighbors = self.get_neighbors(box, 10, 20)
            self.logger.debug('box: %s' % str(box))
            self.logger.debug('# of neighbors: %d' % len(neighbors))
            if len(neighbors) == 0:
                self.boxes.remove(box)

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

    def write_self_boxes_data_to_txt_file(self, outdir):
        with open(ku.mkFilename(
                  self, '_self_boxes', outdir, '.txt'), 'w') as f:
            f.write("self.boxes\n")
            for box in self.boxes:
                f.write(str(box) + "\n")
            f.write("\n")

    def in_margin(self, box, le, ri, up, lo):
        x1, y1 = box[0:2]
        x2, y2 = map(sum, zip(box[0:2], box[2:4]))
        return (y2 < up) or (y1 > lo) or (x2 < le) or (x1 > ri)

    def sweep_boxes_in_page_margin(self, mgn=None):
        """
        pageの余白に存在すると思われるboxは排除
        box: [x, y, w, h]
        """

        if mgn:
            self.pgmgn_x, self.pgmgn_y = mgn

        left_mgn = self.width * self.pgmgn_x
        right_mgn = self.width * (1 - self.pgmgn_x)
        upper_mgn = self.height * self.pgmgn_y
        lower_mgn = self.height * (1 - self.pgmgn_y)

        self.boxes = [x for x in self.boxes if not self.in_margin(x,
                           left_mgn, right_mgn, upper_mgn, lower_mgn)]

    def dispose_boxes(self, debug=False):
        """
        self.boxesから消せるものは消していく
        """
        # w, h どちらかが200以上のboxは排除
        # これはgraphの存在するページでは問題か？
        if "toobig" in self.p["page"]:
            toobig_w, toobig_h = self.p['page']['toobig']
        else:
            toobig_w, toobig_h = [200, 200]
        self.boxes = [x for x in self.boxes
                      if (x[2] < toobig_w) and (x[3] < toobig_h)]

        self.sweep_boxes_in_page_margin()

        # 他のboxに包含されるboxは排除
        self.sweep_included_boxes()

        # 小さく、隣接するもののないboxは排除
        self.sweep_maverick_boxes()

    def collect_boxes(self):
        """
        bounding boxを包含するboxに統合し、文字を囲むboxの取得を試みる
        """
        self.logger.debug('enterd into KnPage#collect_boxes')
        if len(self.boxes) == 0:
            self.getBoxesAndCentroids()

        self.dispose_boxes()

        adjs = []
        while len(self.boxes) > 0:
            abox = self.boxes.pop()
            adjs = self.get_adj_boxes(self.boxes, abox)
            for x in adjs:
                if x in self.boxes:
                    self.boxes.remove(x)
            adjs.append(abox)
            if len(adjs) > 0:
                wrapper = self.get_boundingBox(adjs)
                if wrapper[2] > self.mcbs and wrapper[3] > self.mcbs:
                    self.collected_boxes.append(wrapper)

    def collect_boxes_with_debug(self, outdir=None):
        """
        bounding boxを包含するboxに統合し、文字を囲むboxの取得を試みる
        """
        self.logger.debug('enterd into KnPage#collect_boxes_with_debug')
        if len(self.boxes) == 0:
            self.getBoxesAndCentroids()

        self.dispose_boxes(debug=True)

        if outdir is None:
            outdir = '/home/skkmania/mnt2/workspace/pysrc/knbnk/data'

        self.write_self_boxes_data_to_txt_file(outdir)

        adjs = []

        with open(outdir + '/collect_boxes_debug_output.txt', 'w') as f:
            while len(self.boxes) > 0:
                f.write('self.boxes: ' + str(len(self.boxes)) + "\n")
                abox = self.boxes.pop()
                f.write('abox : ' + str(abox) + "\n")
                adjs = self.get_adj_boxes(self.boxes, abox)
                f.write('adjs : ' + str(adjs) + "\n")
                for x in adjs:
                    if x in self.boxes:
                        self.boxes.remove(x)
                f.write('len of self.boxes after remove : '
                        + str(len(self.boxes)) + "\n")
                f.write('self.boxes after remove: '
                        + str(self.boxes) + "\n")
                adjs.append(abox)
                f.write('adjs after append: ' + str(adjs) + "\n")
                if len(adjs) > 0:
                    wrapper = self.get_boundingBox(adjs)
                    f.write('wrapper : '
                            + str(wrapper) + "\n")
                    if wrapper[2] > self.mcbs and wrapper[3] > self.mcbs:
                        self.collected_boxes.append(wrapper)
                        f.write('self.collected_boxes : '
                            + str(self.collected_boxes) + "\n")

    def write_collected_boxes_to_file(self, outdir=None):
        if not hasattr(self, 'collected_boxes'):
            self.collect_boxes()

        if outdir is None:
            outdir = self.parameters['pagedir']

        om = np.zeros(self.img.shape, np.uint8)
        for box in self.collected_boxes:
            x, y, w, h = box
            cv2.rectangle(om, (x, y), (x + w, y + h), [0, 0, 255])
        cv2.imwrite(ku.mkFilename(self, '_collected_box', outdir), om)

    def write_original_with_collected_boxes_to_file(self, outdir=None):
        if not hasattr(self, 'collected_boxes'):
            self.collect_boxes()
            self.boxes = self.collected_boxes
            self.collect_boxes()
            #self.boxes = self.collected_boxes
            #self.collect_boxes()

        if outdir is None:
            outdir = self.parameters['pagedir']

        self.orig_w_collected = self.img.copy()
        om = self.orig_w_collected
        for box in self.collected_boxes:
            x, y, w, h = box
            cv2.rectangle(om, (x, y), (x + w, y + h), [0, 0, 255])
        cv2.imwrite(ku.mkFilename(self, '_orig_w_collected_box', outdir), om)

    def intersect(self, box1, box2, x_margin=None, y_margin=None):
        """
        box1 と box2 が交わるか接するならtrueを返す。
        marginを指定することですこし離れていても接すると判定.
        """
        if 'ismgn' in self.p['page']:
            xm, ym = self.p['page']['ismgn']
        else:
            xm, ym = (20, 8)        # default

        if x_margin is not None:
            xm = x_margin
        if y_margin is not None:
            ym = y_margin
        ax1, ay1, w1, h1 = box1
        ax2 = ax1 + w1
        ay2 = ay1 + h1
        bx1, by1, w2, h2 = box2
        bx2 = bx1 + w2
        by2 = by1 + h2

        if self.h_apart(ax1, ax2, bx1, bx2, xm):
            return False
        elif self.v_apart(ay1, ay2, by1, by2, ym):
            return False
        else:
            return True

    def h_apart(self, ax1, ax2, bx1, bx2, xm):
        return ax2 < (bx1 - xm) or (bx2 + xm) < ax1

    def v_apart(self, ay1, ay2, by1, by2, ym):
        return ay2 < (by1 - ym) or (by2 + ym) < ay1

    def estimate_char_size(self):
        self.logger.debug("# of collected_boxes: %d" % len(self.collected_boxes))
        self.logger.debug("# of centroids: %d" % len(self.centroids))
        self.square_like_boxes = [x for x in self.collected_boxes if
                             (x[2] * 0.8) < x[3] < (x[2] * 1.2)]
        self.logger.debug("# of square_like_boxes: %d"
                          % len(self.square_like_boxes))
        self.estimated_width = max(map(lambda x: x[2], self.square_like_boxes))
        self.estimated_height = max(map(lambda x: x[3], self.square_like_boxes))
        self.logger.debug('estimated_width: %d' % self.estimated_width)
        self.logger.debug('estimated_height: %d' % self.estimated_height)

    def estimate_vertical_lines(self):
        """
        collected_boxesの重心をソートして、
        ｘ座標がジャンプしているところ
        (経験上、同じ行ならば20 pixel以上離れない）
        (ここは試行錯誤が必要か？ルビや句点を同じ行とするための工夫？）
        が行の切れ目だと判定し、
        collected_boxesをグループ分けする
        """
        self.centroids = map(lambda x: (x[0] + x[2] / 2, x[1] + x[3] / 2),
                             self.collected_boxes)
        self.square_centroids = map(lambda x: (x[0] + x[2] / 2, x[1] + x[3] / 2),
                             self.square_like_boxes)
        self.logger.debug("# of square_centroids: %d"
                          % len(self.square_centroids))
        self.logger.debug("square_centroids: %s" % str(self.square_centroids))
        self.square_centroids.sort(key=itemgetter(0,1))
        self.box_by_v_lines = {}
        self.box_by_v_lines[0] = [self.square_centroids[0]]
        line_idx = 0
        for c in self.square_centroids[1:]:
            if c[0] - self.box_by_v_lines[line_idx][-1][0] <= 20:

                self.box_by_v_lines[line_idx].append(c)
            else:
                line_idx += 1
                self.box_by_v_lines[line_idx] = [c]

        self.logger.debug('box_by_v_lines: %s' % str(self.box_by_v_lines))

    def rotate_image(self):
        image_center = tuple(np.array(self.img.shape[0:2]) / 2)
        dsize = tuple(reversed(np.array(self.img.shape[0:2])))
        if self.estimated_angle > 0:
            degree = 180 * (np.pi / 2 - np.arctan(self.estimated_angle)) / np.pi
            degree = degree * (-1.0)
        else:
            angle = (-1.0) * self.estimated_angle
            degree = 180 * (np.pi / 2 - np.arctan(angle)) / np.pi

        rot_mat = cv2.getRotationMatrix2D(image_center, degree, 1.0)
        self.rotated_img = cv2.warpAffine(self.img, rot_mat,
                                dsize, flags=cv2.INTER_LINEAR)

    def estimate_rotate_angle(self):
        slopes = []
        for k, v in self.box_by_v_lines.items():
            if len(v) > 10:
                xi = map(itemgetter(0),v)
                yi = map(itemgetter(1),v)
                results = stats.linregress(xi,yi)
                slopes.append(results[0])

        self.logger.debug("slopes: %s" % str(slopes))
        self.estimated_slope = np.mean(slopes)
        self.logger.debug("avg of slopes: %f" % self.estimated_slope)
        self.estimated_angle = np.arctan(self.estimated_slope)
        self.logger.debug("estimated_angle: %f" % self.estimated_angle)

    def write_rotated_img_to_file(self, outdir=None, fix=None):
        if outdir is None:
            outdir = self.parameters['pagedir']
        cv2.imwrite(ku.mkFilename(self, '_rotated%s' % fix, outdir),
                    self.rotated_img)

    def in_margin(self, box, le, ri, up, lo):
        x1, y1 = box[0:2]
        x2, y2 = map(sum, zip(box[0:2], box[2:4]))
