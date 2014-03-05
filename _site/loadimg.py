try:
  from opencv.cv import *
  from opencv.highgui import *


# Different OpenCV installs name their packages differently.
#
except:
  from cv import *

if __name__ == '__main__':
  import sys
#
# 1 = Force the image to be loaded as RGB
#
img = LoadImage (sys.argv[1], 1)
NamedWindow ('img')
ShowImage ('img', img)
WaitKey ()

#
# Canny and Harris expect grayscale  (8-bit) input.
# Convert the image to grayscale.  This is a two-step process:
#   1.  Convert to 3-channel YCbCr image
#   2.  Throw away the chroma (Cb, Cr) and keep the luma (Y)
#
yuv = CreateImage(GetSize(img), 8, 3)
gray = CreateImage(GetSize(img), 8, 1)
CvtColor(img, yuv, CV_BGR2YCrCb)
Split(yuv, gray, None, None, None)

canny = CreateImage(GetSize(img), 8, 1)
Canny(gray, canny, 50, 200)
NamedWindow ('canny')
ShowImage ('canny', canny)
WaitKey()

#
# The Harris output must be 32-bit float.
#
harris = CreateImage (GetSize(img), IPL_DEPTH_32F, 1)
CornerHarris(gray, harris, 5, 5, 0.1)
NamedWindow ('harris')
ShowImage ('harris', harris)
WaitKey()
