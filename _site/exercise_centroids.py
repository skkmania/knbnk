# -*- coding: utf-8 -*-
#
#  exercise_centroids.py
#    bounding_boxesのcentroidsの構造と操作を練習するためのスクリプト
#    pdb で 変数を眺めたりすることを想定している
#
#
import sys
import numpy as np
import cv2
from operator import itemgetter, attrgetter

def separate(arr, x, thresh=15):
  if x[1] - arr[-1][-1][1] < thresh:
    arr[-1].append(x)
  else:
    arr.append([x])
  return arr
 

# contourの配列を返す
def get_contours(img, thresh_low=50, thresh_high=255):
  height, width, depth = img.shape
  gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
  ret,thresh = cv2.threshold(gray, thresh_low, thresh_high, 0)
  contours, hierarchy = cv2.findContours(thresh,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
  return (contours, height, width)

# サイズが box_min から box_max のbounding box の重心の配列を返す
def get_centroids(contours, height, width, box_min=16, box_max=48):
  centroids = []
  for cnt in contours:
    x,y,w,h = cv2.boundingRect(cnt)
    if (int(w) in range(box_min, box_max)) or (int(h) in range(box_min, box_max)):
      centroids.append((x+w/2, y+h/2))
  return centroids


infilename = sys.argv[1]

#Load image
img = cv2.imread(infilename)

# get centroids
contours, height, width = get_contours(img)
centroids = get_centroids(contours, height, width)

# print centroids
for p in sorted(centroids,key=itemgetter(1,0)):
  print str(p[0]) + ", " + str(p[1])

sorted_centroids = sorted(centroids,key=itemgetter(1,0))

grouped_centroids = reduce(separate, sorted_centroids, [sorted_centroids[0:1]])

cnt = 0
for ar in grouped_centroids:
  print "group " + str(cnt)
  for p in ar:
    print "  " + str(p[0]) + ", " + str(p[1])
  cnt = cnt + 1
 
