# -*- coding: utf-8 -*-
#
#  resize_and_contours.py
#
#
import sys
import numpy as np
import cv2
from operator import itemgetter, attrgetter

def separate(arr, x):
  if x[1] - arr[-1][-1][1] < 15:
    arr[-1].append(x)
  else:
    arr.append([x])
  return arr
 
#処理時間節約のためminimatという縮小画像をつくり4隅を計算する
def minify(img, scale):
  resize(img, minimat, Size(), scale, scale, interpolation) 
  return minimat

# contourの配列を返す
def get_contours(img, thresh_low=50, thresh_high=255):
  height, width, depth = img.shape
  gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
  ret,thresh = cv2.threshold(gray, thresh_low, thresh_high, 0)
  contours, hierarchy = cv2.findContours(thresh,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
  reuturn (contours, height, width)

# bounding boxを描いた画像を返す
def write_boundingboxes(contours, height, width):
  om    = np.zeros((height,width,3), np.uint8)
  for cnt in contours:
    x,y,w,h = cv2.boundingRect(cnt)
    cv2.rectangle(om, (x, y), (x+w, y+h), [0,255,0])
  reuturn om

# サイズが box_min から box_max のbounding box の重心の配列を返す
def get_centroids(contours, height, width, box_min, box_max):
  centroids = []
  for cnt in contours:
    x,y,w,h = cv2.boundingRect(cnt)
    if (int(w) in range(box_min, box_max)) or (int(h) in range(box_min, box_max)):
      centroids.append((x+w/2, y+h/2))
  return centroids

# centoridsを描いた画像を返す
def write_centroids(centroids, height, width):
  cents = np.zeros((height,width,3), np.uint8)
  for cent in centroids:
    cv2.circle(cents, cent, 5, [0,255,0])
  return cents

infilename = sys.argv[1]
outfilename = 'conts_' + infilename
centsfilename = 'cents_' + infilename
maskfilename = 'mask_' + infilename
meanfilename = 'mean_' + infilename

#Load image
img = cv2.imread(infilename)
height, width, depth = im.shape

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
 
################################
#
 




sorted_centroids = sorted(centroids,key=itemgetter(1,0))

grouped_centroids = reduce(separate, sorted_centroids, [sorted_centroids[0:1]])

cnt = 0
for ar in grouped_centroids:
  print "group " + str(cnt)
  for p in ar:
    print "  " + str(p[0]) + ", " + str(p[1])
  cnt = cnt + 1
 

