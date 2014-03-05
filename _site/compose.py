import sys
import numpy as np
import cv2

# box1 > box2 ?
#def contain(box1, box2):
#  x1,y1,w1,h1 = box1
#  x2,y2,w2,h2 = box2
#  if w1 < w2:
#    if h1 < h2:
#      if x1 > (x2+w2):
#        return '1o2'
#      elif x1 > x2:
#        
#
#      return false
#    else:
#      return
#  else:


infilename = sys.argv[1]
outfilename = 'out_' + infilename
im = cv2.imread(infilename)
height, width, depth = im.shape
om = np.zeros((height,width,3), np.uint8)
imgray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
edges = cv2.Canny(imgray,100,150)
#contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
contours, hierarchy = cv2.findContours(edges,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)

for cnt in contours:
  x,y,w,h = cv2.boundingRect(cnt)
  cv2.rectangle(om, (x, y), (x+w, y+h), [0,255,0])

cv2.imwrite(outfilename, om)

om2 = np.zeros((height,width,3), np.uint8)
box1 = np.array([[[10, 10]], [[ 10, 30]], [[ 30, 10]], [[30, 30]]] )
box2 = np.array([[[40, 20]], [[ 40, 50]], [[ 70, 20]], [[70, 50]]] )
box3 = np.array([[[20, 40]], [[ 20, 70]], [[ 50, 40]], [[50, 70]]] )
cv2.rectangle(om2, (10,10), (30,30), [0,255,0])
cv2.rectangle(om2, (40,20), (70,50), [255,0,0])
cv2.rectangle(om2, (20,40), (50,70), [200,0,0])
total = np.append(box3, np.append(box2,box1,axis=0), axis=0)
x,y,w,h = cv2.boundingRect(total)
cv2.rectangle(om2, (x,y), (x+w, y+h), [0,0,255])

cv2.imwrite('append_' + outfilename, om2)
