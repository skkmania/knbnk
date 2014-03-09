# -*- coding: utf-8 -*-
#      params_file :  parameterをjson形式であらわしたテキストファイルboundingRectの大きさ指定
#      params_file の書式 : 
#        { "boundingRect" : [min, max],                    # boundingRect の大きさ指定
#          "mode"         : findContoursのmode,            # EXTERNAL, LIST, CCOMP, TREE
#          "method"       : findContoursのmethod,          # NONE, SIMPLE, L1, KCOS
#                               以下の3つは排他。どれかひとつを指定。配列内の意味はopencvのdocを参照のこと
#          "canny"        : [threshold1, threshold2],
#          "threshold"    : [thresh, maxval, type],
#          "adaptive"     : [maxval, method, type, blockSize, C]
#        }
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
from operator import itemgetter, attrgetter

class KnPage:

  def __init__(self, fname):
    if os.path.exists(fname):
      self.img = cv2.imread(fname)
      self.original_file_name = fname
      if self.img == None:
          raise
      else:
        self.height, self.width, self.depth = self.img.shape
        self.centroids = []
    else:
      raise
     


  def divide(self):
    self.left = None
    self.right = None

  def write(self, outfilename, om=None):
    if om == None:
        om = self.img
    cv2.imwrite(outfilename, om)

  def update(self, v):
    self.val = v

  def separate(self, arr, x):
    if x[1] - arr[-1][-1][1] < 15:
      arr[-1].append(x)
    else:
      arr.append([x])
    return arr

  def mkFilename(self, fix, outdir=None):
    dirname = os.path.dirname(self.original_file_name) 
    basename = os.path.basename(self.original_file_name) 
    if fix == 'data':
      name, ext = os.path.splitext(basename) 
      name = name + '_data'
      ext = '.txt'
    else:
      name, ext = os.path.splitext(basename) 
      name = name + fix

    if outdir == None:
      return os.path.join(dirname, name + ext)
    else:
      return os.path.join(outdir, name + ext)

  # サイズが box_min から box_max のbounding box の重心の配列を返す
  def getCentroids(self, box_min=16, box_max=48):
    if not hasattr(self, 'contours'):
      self.getContours()

    for cnt in self.contours:
      x,y,w,h = cv2.boundingRect(cnt)
      if (int(w) in range(box_min, box_max)) or (int(h) in range(box_min, box_max)):
        self.centroids.append((x+w/2, y+h/2))

  # contourの配列を返す
  def getContours(self, thresh_low=50, thresh_high=255):
    self.gray = cv2.cvtColor(self.img,cv2.COLOR_BGR2GRAY)
    ret,self.thresh = cv2.threshold(self.gray, thresh_low, thresh_high, 0)
    self.contours, self.hierarchy = cv2.findContours(self.thresh,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)

  def writeContour(self):
    self.img_of_contours = np.zeros(self.img.shape,np.uint8)
    for point in self.contours:
      x,y = point[0][0]
      cv2.circle(self.img_of_contours, (x,y), 1, [0,0,255])

  def write_contours_bounding_rect_to_file(self, outdir=None):
    if not hasattr(self, 'contours'):
      self.getContours()
    om = np.zeros(self.img.shape,np.uint8)
    for cnt in self.contours:
      x,y,w,h = cv2.boundingRect(cnt)
      cv2.rectangle(om, (x, y), (x+w, y+h), [0,255,0])
      if (int(w) in range(60,120)) or (int(h) in range(60,120)):
        self.centroids.append((x+w/2, y+h/2))
        cv2.circle(om, (int(x+w/2), int(y+h/2)), 5, [0,255,0])
    self.write(self.mkFilename('_cont_rect', outdir), om)

  def write_data_file(self, outdir):
    if not hasattr(self, 'contours'):
      self.getContours()
    outfilename = self.mkFilename('data', outdir)
    f = open(outfilename, 'w')
    f.write("contours\n")
    for cnt in self.contours:
      f.writelines(str(cnt))
      f.write("\n")
  
    f.write("\n\nhierarchy\n")
    for hic in self.hierarchy:
      f.writelines(str(hic))
      f.write("\n")
    f.close()

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
