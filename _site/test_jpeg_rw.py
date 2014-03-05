import sys
import numpy as np
import cv2
 
infilename = sys.argv[1]
outfilename = 'out_' + infilename
im = cv2.imread(infilename)
#im_any = cv2.imread(infilename, cv2.CV_LOAD_IMAGE_ANYDEPTH)
im_any = cv2.imread(infilename, -1)
#im_col = cv2.imread(infilename, cv2.LOAD_IMAGE_COLOR)
im_col = cv2.imread(infilename, 1)
#im_gra = cv2.imread(infilename, cv2.LOAD_IMAGE_GRAYSCALE)
im_gra = cv2.imread(infilename, 0)
im_cvt = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
 
 
           
cv2.imwrite('nospec_'+outfilename, im)
cv2.imwrite('cvt_'+outfilename, im_cvt)
cv2.imwrite('any_100_'+outfilename, im_any, [cv2.IMWRITE_JPEG_QUALITY, 100])
cv2.imwrite('any_80_'+outfilename, im_any, [cv2.IMWRITE_JPEG_QUALITY, 80])
cv2.imwrite('any_50_'+outfilename, im_any, [cv2.IMWRITE_JPEG_QUALITY, 50])
cv2.imwrite('any_30_'+outfilename, im_any, [cv2.IMWRITE_JPEG_QUALITY, 30])
cv2.imwrite('any_10_'+outfilename, im_any, [cv2.IMWRITE_JPEG_QUALITY, 10])
cv2.imwrite('gra_100_'+outfilename, im_gra, [cv2.IMWRITE_JPEG_QUALITY, 100])
cv2.imwrite('gra_80_'+outfilename, im_gra, [cv2.IMWRITE_JPEG_QUALITY, 80])
cv2.imwrite('gra_50_'+outfilename, im_gra, [cv2.IMWRITE_JPEG_QUALITY, 50])
cv2.imwrite('gra_30_'+outfilename, im_gra, [cv2.IMWRITE_JPEG_QUALITY, 30])
cv2.imwrite('gra_10_'+outfilename, im_gra, [cv2.IMWRITE_JPEG_QUALITY, 10])
cv2.imwrite('gra_05_'+outfilename, im_gra, [cv2.IMWRITE_JPEG_QUALITY, 5])
