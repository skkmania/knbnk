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
 
infilename = sys.argv[1]
outfilename = 'conts_' + infilename
centsfilename = 'cents_' + infilename
maskfilename = 'mask_' + infilename
meanfilename = 'mean_' + infilename

im = cv2.imread(infilename)
height, width, depth = im.shape
om    = np.zeros((height,width,3), np.uint8)
cents = np.zeros((height,width,3), np.uint8)
imgray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
ret,thresh = cv2.threshold(imgray,200,255,0)
#contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
contours, hierarchy = cv2.findContours(thresh,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)

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
 
