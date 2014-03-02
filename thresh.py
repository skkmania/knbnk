import sys
import numpy as np
import cv2
 
infilename = sys.argv[1]
outfilename = 'out_' + infilename
im = cv2.imread(infilename)
img = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
 
ret,thresh1 = cv2.threshold(img,63,255,cv2.THRESH_BINARY)
ret,thresh2 = cv2.threshold(img,127,255,cv2.THRESH_BINARY_INV)
ret,thresh3 = cv2.threshold(img,127,255,cv2.THRESH_TRUNC)
ret,thresh4 = cv2.threshold(img,127,255,cv2.THRESH_TOZERO)
ret,thresh4_1 = cv2.threshold(img,63,255,cv2.THRESH_TOZERO)
ret,thresh5 = cv2.threshold(img,127,255,cv2.THRESH_TOZERO_INV)
 
th6 = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_MEAN_C,\
                cv2.THRESH_BINARY,11,2)
th7 = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
                cv2.THRESH_BINARY,11,2)
  
  
           

cv2.imwrite('1_'+outfilename, thresh1)
cv2.imwrite('4_100'+outfilename, thresh4, [cv2.IMWRITE_JPEG_QUALITY, 100])
cv2.imwrite('4_90'+outfilename, thresh4, [cv2.IMWRITE_JPEG_QUALITY, 90])
cv2.imwrite('4_80'+outfilename, thresh4, [cv2.IMWRITE_JPEG_QUALITY, 80])
cv2.imwrite('4_1_'+outfilename, thresh4_1)
cv2.imwrite('6_'+outfilename, th6)
cv2.imwrite('7_'+outfilename, th7)
