# -*- coding: utf-8 -*- 
import os,sys
import cv2
import numpy as np
import os.path

def ch(filename, blockSize, ksize, k, threshold):
  name, ext = os.path.splitext(filename)
  outfilename = name + "_bs_" + str(blockSize) + "_ks_" + str(ksize) + "_k_" + str(k) + "_th_" + str(threshold) + ext
  img = cv2.imread(filename)
  gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
  
  gray = np.float32(gray)
  dst_ch = cv2.cornerHarris(gray,blockSize, ksize, k)
  
  #result is dilated for marking the corners, not important
  dst_di = cv2.dilate(dst_ch,None)
  
  # Threshold for an optimal value, it may vary depending on the image.
  img[dst_di>threshold*dst_di.max()]=[0,0,255]
  
  cv2.imwrite(outfilename, img)


filename = sys.argv[1]

# blockSizeを大きくすると検出するコーナーの数が増える
#ch(filename, 2, 3, 0.04, 0.01)
#ch(filename, 3, 3, 0.04, 0.01)
#ch(filename, 4, 3, 0.04, 0.01)

# thresholdを小さくすると検出するコーナーの数が増える
#ch(filename, 2, 3, 0.04, 0.01)
#ch(filename, 2, 3, 0.04, 0.005)
#ch(filename, 2, 3, 0.04, 0.001)

# ksize(kernel size)(must be odd and under 32)を変えてもコーナーの数にあまり変化はない
#ch(filename, 2, 5, 0.04, 0.01)
#ch(filename, 2, 7, 0.04, 0.01)
#ch(filename, 2, 9, 0.04, 0.01)

# k(Harris detector free parameter in the equation)を小さくすると検出するコーナーの数が増える
ch(filename, 2, 3, 0.02, 0.01)
ch(filename, 2, 3, 0.06, 0.01)
ch(filename, 2, 3, 0.08, 0.01)
