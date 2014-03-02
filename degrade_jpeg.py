import sys
import numpy as np
import cv2
 
infilename = sys.argv[1]
qual = sys.argv[2]
outfilename = 'out_' + infilename
im = cv2.imread(infilename)
#im_gra = cv2.imread(infilename, cv2.LOAD_IMAGE_GRAYSCALE)
im_gra = cv2.imread(infilename, 0)
im_cvt = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
 
cv2.imwrite('gra_' + qual + '_' + outfilename, im_gra, [cv2.IMWRITE_JPEG_QUALITY, int(qual)])
