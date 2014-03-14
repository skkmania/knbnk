# -*- coding: utf-8 -*-
# params_file :  parameterをjson形式であらわしたテキストファイルboundingRectの大きさ指定
# params_file の書式 :
#   {
#     "fname"        : "text",                 # img file name
#     "datadir"      : "text",                 # data所在directory
#     "boundingRect" : [min, max],             # boundingRect の大きさ指定
#     "mode"         : findContoursのmode,     # EXTERNAL, LIST, CCOMP, TREE
#     "method"       : findContoursのmethod,   # NONE, SIMPLE, L1, KCOS
#   以下の3つは排他。どれかひとつを指定。配列内の意味はopencvのdocを参照のこと
#     "canny"        : [threshold1, threshold2],
#     "threshold"    : [thresh, maxval, type],
#     "adaptive"     : [maxval, method, type, blockSize, C]
#   }
#
#  5つのfileを生成する
#      出力0 :  statitics file  contourなどのデータのテキストファイル
#      出力1 :  findContourを適用する直前の画像のファイル
#      出力2 :  元の画像にcontourを重ね書きしたファイル
#      出力3 :  元の画像にcontourとそのboundingRectを重ね書きしたファイル
#      出力4 :  contourのみを書いたファイル
#      出力5 :  contourとそのboundingRectを重ね書きしたファイル

#import sys
import numpy as np

import cv2
import json
import os.path
#from operator import itemgetter, attrgetter


class KnPage:

    def __init__(self, fname, datadir=None, params=None):
        if os.path.exists(fname):
            self.img = cv2.imread(fname)
            self.original_file_name = fname
            if self.img is None:
                raise
            else:
                self.height, self.width, self.depth = self.img.shape
                self.centroids = []
                self.boxes = []
                if params:
                    if os.path.exists(params):
                        self.read_params(params)
                    else:
                        raise
        else:
            raise

    def read_params(self, params):
        with open(params) as f:
            lines = f.readlines()
        self.parameters = json.loads(''.join(lines))
        self.outfilename = self.parameters['outfilename']

    def divide(self):
        self.left = None
        self.right = None

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
        dirname = os.path.dirname(self.original_file_name)
        basename = os.path.basename(self.original_file_name)
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
            if (int(w) in range(box_min, box_max)) or (int(h) in range(box_min, box_max)):
                self.centroids.append((x + w / 2, y + h / 2))

    # contourの配列を返す
    def getContours(self, thresh_low=50, thresh_high=255):
        self.gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        if hasattr(self, 'parameters'):
            if 'threshold' in self.parameters:
                thresh_low, thresh_high, typeval = self.parameters['threshold']
                ret, self.thresh = cv2.threshold(self.gray,
                                                 thresh_low, thresh_high, typeval)
            elif 'canny' in self.parameters:
                minval, maxval = self.parameters['canny']
                self.thresh = cv2.Canny(self.gray, minval, maxval)
            elif 'adaptive' in self.parameters:
                self.thresh = cv2.adaptiveThreshold(self.gray,
                                                    self.parameters['adaptive'])
        else:
            ret, self.thresh = cv2.threshold(self.gray, thresh_low, thresh_high, 0)

        self.contours, self.hierarchy = cv2.findContours(self.thresh,
                                                         cv2.RETR_LIST,
                                                         cv2.CHAIN_APPROX_SIMPLE)

    def writeContour(self):
        self.img_of_contours = np.zeros(self.img.shape,np.uint8)
        for point in self.contours:
            x,y = point[0][0]
            cv2.circle(self.img_of_contours, (x,y), 1, [0,0,255])

    def write_contours_bounding_rect_to_file(self, outdir=None):
        if not hasattr(self, 'contours'):
            self.getContours()
        om = np.zeros(self.img.shape, np.uint8)
        for cnt in self.contours:
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(om, (x, y), (x + w, y + h), [0, 255, 0])
            if (int(w) in range(60, 120)) or (int(h) in range(60, 120)):
                self.centroids.append((x + w / 2, y + h / 2))
                cv2.circle(om, (int(x + w / 2), int(y + h / 2)), 5, [0, 255, 0])
        self.write(self.mkFilename('_cont_rect', outdir), om)

    def write_boxes_to_file(self, outdir):
        om = np.zeros(self.img.shape,np.uint8)
        for box in self.boxes:
            x,y,w,h = box
            cv2.rectangle(om, (x, y), (x+w, y+h), [0,255,0])
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
      self.write(outfilename,self.thresh)

    def write_original_with_contour_file(self, outdir):
      if not hasattr(self, 'contours'):
        self.getContours()
      self.orig_w_cont = self.img.copy()
      for point in self.contours:
        x,y = point[0][0]
        cv2.circle(self.orig_w_cont, (x,y), 1, [0,0,255])
      outfilename = self.mkFilename('_orig_w_cont', outdir)
      self.write(outfilename,self.orig_w_cont)

    def write_original_with_contour_and_rect_file(self, outdir):
      if not hasattr(self, 'contours'):
        self.getContours()
      self.orig_w_cont_and_rect = self.img.copy()
      om = self.orig_w_cont_and_rect
      for cnt in self.contours:
        x,y,w,h = cv2.boundingRect(cnt)
        cv2.rectangle(om, (x, y), (x+w, y+h), [0,255,0])
        if (int(w) in range(60,120)) or (int(h) in range(60,120)):
          self.centroids.append((x+w/2, y+h/2))
          cv2.circle(om, (int(x+w/2), int(y+h/2)), 5, [0,255,0])
        cx,cy = cnt[0][0]
        cv2.circle(om, (cx,cy), 2, [0,0,255])
      outfilename = self.mkFilename('_orig_w_cont_and_rect', outdir)
      self.write(outfilename,self.orig_w_cont_and_rect)

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

        ax1,ay1,w1,h1 = box1
        ax2 = ax1 + w1
        ay2 = ay1 + h1
        bx1,by1,w2,h2 = box2
        bx2 = bx1 + w2
        by2 = by1 + h2

        if (ax1 <= bx1) and (bx2 <= ax2) and (ay1 <= by1) and (by2 <= ay2):
          return True
        else:
          return False

    def intersect(self, box1, box2, x_margin = 20, y_margin = 8):
        """
           box1 と box2 が交わるか接するならtrueを返す。
           marginを指定することですこし離れていても交わっていると判定させることができる
        """
        xm = x_margin
        ym = y_margin
        ax1,ay1,w1,h1 = box1
        ax2 = ax1 + w1
        ay2 = ay1 + h1
        bx1,by1,w2,h2 = box2
        bx2 = bx1 + w2
        by2 = by1 + h2

        if (bx1 in range(ax1 - xm, ax2 + xm)) and (by1 in range(ay1 - ym, ay2 + ym)):
            return True
        if (bx2 in range(ax1 - xm, ax2 + xm)) and (by2 in range(ay1 - ym, ay2 + ym)):
            return True
        if (bx2 in range(ax1 - xm, ax2 + xm)) and (by1 in range(ay1 - ym, ay2 + ym)):
            return True
        if (bx1 in range(ax1 - xm, ax2 + xm)) and (by2 in range(ay1 - ym, ay2 + ym)):
            return True
        if (ax1 in range(bx1 - xm, bx2 + xm)) and (ay1 in range(by1 - ym, by2 + ym)):
            return True
        if (ax2 in range(bx1 - xm, bx2 + xm)) and (ay2 in range(by1 - ym, by2 + ym)):
            return True
        if (ax2 in range(bx1 - xm, bx2 + xm)) and (ay1 in range(by1 - ym, by2 + ym)):
            return True
        if (ax1 in range(bx1 - xm, bx2 + xm)) and (ay2 in range(by1 - ym, by2 + ym)):
            return True

        return False

    def get_boundingBox(self, boxes):
        # 入力のboxの形式は(x,y,w,h)
        # 出力のboxの形式も(x,y,w,h)
        # (x,y,w,h) -> (x,y,x+w,y+h)
        target = [(x,y,x+w,y+h) for (x,y,w,h) in boxes]
        x1,y1,d1,d2 = map(min, zip(*target))
        d1,d2,x2,y2 = map(max, zip(*target))
        # (x,y,x+w,y+h) -> (x,y,x,y)
        return (x1,y1,x2-x1,y2-y1)

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
      return reduce(lambda a,b:a+(self.flatten(b) if hasattr(b,'__iter__') else [b]), i, [])

    def show_message(f):
        def wrapper():
            print("function called")
            return f()
        return wrapper

    def get_adj_boxes(self, boxes, abox):
      if abox in boxes: boxes.remove(abox)

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
          f.write(str(box)+"\n")
        f.write("\n")

    def collect_boxes(self):
      """ bounding boxを包含するboxに統合し、文字を囲むboxの取得を試みる"""

      if len(self.boxes) == 0:
          self.getCentroids()

      # w, h どちらかが200以上のboxは排除
      self.boxes = [x for x in self.boxes if (x[2] < 200) and (x[3] < 200)]

      self.write_self_boxes_to_file('/home/skkmania/mnt2/workspace/pysrc/knbnk/data')    #for debug

      self.collected_boxes = []
      adjs = []

      f = open('while_process.txt', 'w')    #for debug
      while len(self.boxes) > 0:
        f.write('len of self.boxes : ' + str(len(self.boxes))+"\n")    #for debug
        abox = self.boxes.pop()
        f.write('abox : ' + str(abox)+"\n")    #for debug
        #temp_boxes = [x for x in self.boxes if self.intersect(abox, x)]
        adjs = self.get_adj_boxes(self.boxes, abox)
        f.write('adjs : ' + str(adjs)+"\n")    #for debug
        for x in adjs:
            if x in self.boxes:  self.boxes.remove(x)
        f.write('len of self.boxes after remove : ' + str(len(self.boxes))+"\n")    #for debug
        f.write('self.boxes after remove: ' + str(self.boxes)+"\n")    #for debug
        adjs.append(abox)
        f.write('adjs after append: ' + str(adjs)+"\n")    #for debug
        if len(adjs) > 0:
          boundingBox = self.get_boundingBox(adjs)
          f.write('boundingBox : ' + str(boundingBox)+"\n")    #for debug
          self.collected_boxes.append(boundingBox)
          f.write('self.collected_boxes : ' + str(self.collected_boxes)+"\n")    #for debug

      f.close()    #for debug

    def write_collected_boxes_to_file(self, outdir=None):
      if not hasattr(self, 'collected_boxes'):
        self.collect_boxes()

      om = np.zeros(self.img.shape,np.uint8)
      for box in self.collected_boxes:
        x,y,w,h = box
        cv2.rectangle(om, (x, y), (x+w, y+h), [0,0,255])
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
            cv2.rectangle(om, (x, y), (x+w, y+h), [0,0,255])
        self.write(self.mkFilename('_orig_w_collected_box', outdir), om)

