---
layout: post
title: 2値化あれこれ
date: 2014-03-17
---
sample 画像とその2値化の結果を方法ごとに示す

##sample

![twletters.jpg](/images/twletters.jpg)

#  "canny"        : [threshold1, threshold2],↲

canny threshold1 = 50,  threshold2 = 200

![twl_can_50_200.jpg](/images/twl_can_LIST_50_200_binarized.jpg)

#  "threshold"    : [thresh, maxval, type],↲
#  "adaptive"     : [maxval, method, type, blockSize, C]↲



同じような処理としてエッジ検出の結果も参考に記しておく。
#  "Sobel"

sobel　（xorder, yorder, aperture_size）＝ (1,0,3)

![twletters.jpg](/images/twl_sobel_-1_0_1.jpg)

sobel　（xorder, yorder, aperture_size）＝ (0,1,3)

![twletters.jpg](/images/twl_sobel_-1_1_0.jpg)

sobel　（xorder, yorder, aperture_size）＝ (1,1,3)

![twletters.jpg](/images/twl_sobel_-1_1_1.jpg)

#  "scharr"

scharr　（xorder, yorder）＝ (1,0)
とは、
sobel　（xorder, yorder, aperture_size）＝ (1,0,Scharr)
とするのと同じ。
![twletters.jpg](/images/twl_sharr_-1_1_0.jpg)

scharr　（xorder, yorder）＝ (0,1)

![twletters.jpg](/images/twl_sharr_-1_0_1.jpg)
