# -*- coding: utf-8 -*-
# imgに近デジの画像を渡すと左右のページの範囲を返す処理 */
#  page_split.py

import sys
import numpy as np
import cv2
from operator import itemgetter, attrgetter

sys.stdout = codecs.getwriter('utf_8')(sys.stdout)
sys.stdin = codecs.getreader('utf_8')(sys.stdin)


# 処理するときの縦サイズ(px).
# 小さいほうが速いけど、小さすぎると小さい線が見つからなくなる.
#cvHoughLines2のパラメータもこれをベースに決める.
SCALE_SIZE = 640.0

# 最低オフセットが存在することを想定する(px).
# 真ん中にある謎の黒い線の上下をtop,bottomに選択しないためのテキトウな処理で使う.
HARD_OFFSET = 32

# ページ中心のズレの許容範囲(px / 2).
#  余白を切った矩形の中心からこの距離範囲の間でページの中心を決める.
CENTER_RANGE = 64

# 中心を決める際に使う線の最大数.
CENTER_SAMPLE_MAX = 1024

# 中心決めるときのクラスタ数 */
CENTER_K = 3
center, center_base, samples;
CvMat *center_samples = cvCreateMat(CENTER_SAMPLE_MAX, 1, CV_32FC1);
CvMat *labels = cvCreateMat(CENTER_SAMPLE_MAX, 1, CV_32SC1);


# リサイズしたエッジ画像から確率的ハフ変換で線を検出する */
def get_lines(img):
  height, width, depth = img.shape
  scale = SCALE_SIZE / height
  small_img = np.zeros((height*scale,width*scale,3), np.uint8)
  cv2.resize(img, small_img)
  small_img_gray = cv2.cvtColor(small_img,cv2.COLOR_BGR2GRAY)
  cv2.canny(small_img_gray, small_img_gray, 50, 200, 3);

  lines = cv2.HoughLines(small_img_gray,OpenCV::CV_HOUGH_PROBABILISTIC, 1, CV_PI / 2, 50, 32, 16)
  #lines = cv2.HoughLines(small_img_gray,OpenCV::CV_HOUGH_PROBABILISTIC,  1, 1.57, 50, 50, 32 )
  return lines


# 余白を切る範囲を決める */
def get_margin(lines, width, height):
  top = 9999
  bottom = 0
  left = 9999
  right = 0
  for line in lines:
    points = line.points
    if (abs(points[0].x - points[1].x) ]]> abs(points[0].y - points[1].y))
      # 横線
      for j in [0,1]:
        if (top > points[j].y and points[j].y > HARD_OFFSET)
          top = points[j].y

      if (bottom < points[j].y and points[j].y < height - HARD_OFFSET)
        bottom = points[j].y
    else
      # 縦線
      for j in [0,1]:
        if (left > points[j].x and points[j].x > HARD_OFFSET)
          left = points[j].x

      if (right < points[j].x and points[j].x < width - HARD_OFFSET)
        right = points[j].x

# 検出した線をimgに描く(debug用)
def write_lines
    CvPoint tmp[2];
    tmp[0] = points[0];
    tmp[1] = points[1];
    tmp[0].x = (int)(points[0].x / scale);
    tmp[0].y = (int)(points[0].y / scale);
    tmp[1].x = (int)(points[1].x / scale);
    tmp[1].y = (int)(points[1].y / scale);
    cvLine(img, tmp[0], tmp[1], CV_RGB (255, 0, 0), 1, 8, 0);

    if (abs(points[0].x - points[1].x) ]]> abs(points[0].y - points[1].y)) {
        cvLine(img, tmp[0], tmp[1], CV_RGB (0, 0, 255), 1, 8, 0);
        } else {
            cvLine(img, tmp[0], tmp[1], CV_RGB (0, 255, 0), 1, 8, 0);
            }
        }
        #endif
        }

         # 左右の分割点を決める */

          # 中心あたりをサンプリング */

           center_base = left + (right - left) / 2;
           center = center_base;
           samples = 0;
           cvZero(center_samples);
           cvZero(labels);
           for (i = 0; i < lines->total; i++) {
               CvPoint *points = (CvPoint *)cvGetSeqElem(lines, i);
               if (abs(points[0].x - points[1].x) < abs(points[0].y - points[1].y))
               {
                 # 縦線 */
                 for (j = 0; j < 2; ++j) {
                   int dist = abs(points[j].x - center_base);
                   if (dist < CENTER_RANGE) {
                     CV_MAT_ELEM(*center_samples, float, samples, 0) = (float)points[j].x;
                     if (++samples >= CENTER_SAMPLE_MAX) {
                       goto _break;
                       }
                     #if _DEBUG
                     { # サンプリングした線をimgに描く(debug用) */
                       CvPoint tmp[2];
                       tmp[0] = points[0];
                       tmp[1] = points[1];
                       tmp[0].x = (int)(points[0].x / scale);
                       tmp[0].y = (int)(points[0].y / scale);
                       tmp[1].x = (int)(points[1].x / scale);
                       tmp[1].y = (int)(points[1].y / scale);
                       cvLine(img, tmp[0], tmp[1], CV_RGB (255, 0, 0), 1, 8, 0);
                       }
                     #endif
                     }
                   }
                 }
               }
           _break:

# クラスタリングして中心を決める */
def take_center:
  if (samples > CENTER_K)
    label_centers[CENTER_K] = {0};
    label_counts[CENTER_K] = {0};

    center_samples->rows = samples;
    labels->rows = samples;
    cvKMeans2(center_samples, CENTER_K, labels, cvTermCriteria(CV_TERMCRIT_ITER, 50, 1.0),
      1, 0, 0, 0, 0);
    for (i = 0; i < samples; ++i) {
      int label = CV_MAT_ELEM(*labels, int, i, 0);
      ++label_counts[label];
      label_centers[label] += CV_MAT_ELEM(*center_samples, float, i, 0);
      }
    for (i = 0; i < CENTER_K; ++i) {
      if (label_counts[i] ]]> 0) {
          label_centers[i] /= label_counts[i];
          }
      }
      qsort(label_centers, CENTER_K, sizeof(float), float_cmp);
      center = (int)label_centers[CENTER_K / 2];
      } else {
          center = center_base;
                              }

          left_page->x = (int)(left / scale);
          left_page->y = (int)(top / scale);
          left_page->width = (int)(center / scale) - left_page->x;
          left_page->height = (int)(bottom / scale) - left_page->y;
          right_page->x = (int)(center / scale);
          right_page->y = (int)(top / scale);
          right_page->width = (int)(right / scale) - right_page->x;
          right_page->height = left_page->height;

           center_samples->rows = CENTER_SAMPLE_MAX;
           labels->rows = CENTER_SAMPLE_MAX;
           cvReleaseImage (&small_img);
           cvReleaseImage (&edges);
           cvReleaseMemStorage (&storage);
           cvReleaseMat(&center_samples);
           cvReleaseMat(&labels);

            return 0;
          }

def output_result:
  # ページの結果を表示してみる
               ret = page_split(img, &left_page, &right_page);
               cvRectangle(img,
                 cvPoint(left_page.x, left_page.y),
                 cvPoint(lefe);
                 left_page->width = (int)(center / scale) - left_page->x;
                 CVft_page->height = (int)(bottom / scale) - left_page->y;
                 rightage.x, right_page.y),
               cvPoint(right_page.x + right_page.width, rile);
               right_page->width = (int)(right / scale) - right_page->x

               cvShowImage= CENTER_SAMPLE_MAX;
               labels->rows = CENTER_SAMPLE_MAX;


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

