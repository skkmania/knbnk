---
layout: post
title: HoughLines
date: 2014-03-22
---
HoughLinesの結果をparameterを変えて示す

##sample

これはあるコマの画像のオリジナル。
この画像から余分な余白を削除したい。

![007.jpeg](/images/Hough/007.jpeg)

しかしこのように大きいままだと計算負荷が大きい。
余白の境界を求めるだけなら縮小してもじゅうぶんに正確な結果が得られる。

![007_small.jpeg](/images/Hough/007_small.jpeg)

#  HoughLinesのparameter↲

## "hough"        : [rho, theta, minimumVote]

###      rho : accuracy of rho.  integerを指定。1 など。↲

###      theta:  accuracy of theta. int(1 - 180)を指定。↲

               np.pi/180 などradianで考えるので、その分母を指定する。↲
               180なら1度ずつ、2なら水平と垂直の直線のみを候補とするという意味↲

###      minimumVote:↲
           lineとみなすため必要な点の数。検出する線の長さに影響する。↲


### Hough rho = 1,  theta = PI/180, minimumVote = 100

thetaを大きくすると、さまざまな角度の線が検出される。

![hough_1_180_100_007](/images/Hough/hough_1_180_100_007_small_img_with_lines.jpeg)

### Hough rho = 1,  theta = PI/2, minimumVote = 100

thetaを2にすると、水平と垂直の線が検出される。
この例のように画像がほぼ水平にある場合はこの程度の値が最も有効だろう。

![hough_1_2_100_007](/images/Hough/hough_1_2_100_007_small_img_with_lines.jpeg)

thetaを2のままにしても、minimumVoteを大きくすると検出できる線が減り、余白をとらえ損なう。

![hough_1_2_150_007](/images/Hough/hough_1_2_150_007_small_img_with_lines.jpeg)


### Hough rho = 1,  theta = PI/90, minimumVote = 150

thetaを90にしても水平と垂直の線が検出される

![hough_1_90_150_007](/images/Hough/hough_1_90_150_007_small_img_with_lines.jpeg)

minimumVoteを大きくすると検出できる線が減り、余白をとらえ損なう。

![hough_1_90_200_007](/images/Hough/hough_1_90_200_007_small_img_with_lines.jpeg)


