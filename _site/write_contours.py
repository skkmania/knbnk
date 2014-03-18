# -*- coding: utf-8 -*-
#
#  write_contours.py
#    Usage:  write_contours.py  infilename [ params_file ]
#      infilename  :  画像ファイル
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

def separate(arr, x):
  if x[1] - arr[-1][-1][1] < 15:
    arr[-1].append(x)
  else:
    arr.append([x])
  return arr
 
def read_options(filename):
  f = open(filename)
  data = f.read()  # ファイル終端まで全て読んだデータを返す
  f.close()
  return json.loads(data)

def write_data_file(contours, hierarchy, name):
  outfilename0 = name + "_data.txt" 
  f = open(filename, 'w')
  f.write("contours")
  for cnt in contours:
    f.writelines(cnt)

  f.write("hierarchy")
  for hic in hierarchy:
    f.writelines(hic)
  f.close()

if sys.argv[2]:
  options = read_options(sys.argv[2])
else:
  options = false

infilename = sys.argv[1]
name, ext = os.path.splitext(infilename)
outfilename1 = name + "_binarized" + ext
outfilename2 = name + "_with_contour" + ext
outfilename3 = name + "_with_contour_and_rect" + ext
outfilename4 = name + "_contour_only" + ext
outfilename5 = name + "_contour_and_rect" + ext
outfilename = 'conts_' + infilename
centsfilename = 'cents_' + infilename
maskfilename = 'mask_' + infilename
meanfilename = 'mean_' + infilename

im = cv2.imread(infilename)
height, width, depth = im.shape
om    = np.zeros((height,width,3), np.uint8)
cents = np.zeros((height,width,3), np.uint8)
imgray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)

if options:
  if options['threshold']:
    thresh, maxval, type = options['threshold']
    ret,thresh = cv2.threshold(imgray,thresh,maxval,type)
  elsif options['canny']:
    threshold1, threshold2 = options['canny']
    thresh = cv2.Canny(imgray,threshold1, threshold2)
  elsif options['adaptive']:
    maxval, method, type, blockSize, c = options['adaptive']
    thresh = cv2.adaptiveThreshold(imgray,maxval,method, type, blockSize, c)

  if options['mode'] == 'EXTERNAL':
    mode = cv2.RETR_EXTERNAL
  elsif options['mode'] == 'LIST':
    mode = cv2.RETR_LIST
  elsif options['mode'] == 'CCOMP':
    mode = cv2.RETR_CCOMP
  elsif options['mode'] == 'TREE':
    mode = cv2.RETR_TREE
  else:
    mode = cv2.RETR_LIST

  if options['method'] == 'NONE':
    method = cv2.CHAIN_APPROX_NONE
  elsif options['method'] == 'SIMPLE':
    method = cv2.CHAIN_APPROX_SIMPLE
  elsif options['method'] == 'L1':
    method = cv2.CHAIN_APPROX_TC89_L1
  elsif options['method'] == 'KCOS':
    method = cv2.CHAIN_APPROX_TC89_KCOS
  else:
    method = cv2.CHAIN_APPROX_SIMPLE

contours, hierarchy = cv2.findContours(thresh,mode,method)
write_data_file(contours, hierarchy, name) 
write_contour_file(contours)
cv2.imwrite(outfilename, om)

centroids = []

for cnt in contours:
  x,y,w,h = cv2.boundingRect(cnt)
  cv2.rectangle(om, (x, y), (x+w, y+h), [0,255,0])
  if (int(w) in range(60,120)) or (int(h) in range(60,120)):
    centroids.append((x+w/2, y+h/2))
    cv2.circle(cents, (int(x+w/2), int(y+h/2)), 5, [0,255,0])

#for h,cnt in enumerate(contours):
#  mask = np.zeros(imgray.shape,np.uint8)
#  cv2.drawContours(mask,[cnt],0,255,-1)
#  mean = cv2.mean(im,mask = mask)

centsgray = cv2.cvtColor(cents,cv2.COLOR_BGR2GRAY)
lines = cv2.HoughLines(centsgray, 1, 1.7, 10)

for line in lines:
  cv2.line(cents, (int(line[0][0]),int(line[0][1])), (int(line[1][0]),int(line[1][1])), 1, 255)

cv2.imwrite(outfilename, om)
cv2.imwrite(centsfilename, cents)
#cv2.imwrite(maskfilename, mask)
#cv2.imwrite(meanfilename, mean)

#for p in sorted(centroids,key=itemgetter(1,0)):
#  print str(p[0]) + ", " + str(p[1])

sorted_centroids = sorted(centroids,key=itemgetter(1,0))

grouped_centroids = reduce(separate, sorted_centroids, [sorted_centroids[0:1]])

cnt = 0
for ar in grouped_centroids:
  print "group " + str(cnt)
  for p in ar:
    print "  " + str(p[0]) + ", " + str(p[1])
  cnt = cnt + 1
 
