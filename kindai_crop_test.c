/* 近代デジタルの画像をページ分割するヤツ(page_split)
　　　opencvを使う.
 */
#if 0
#include <cv.h>
#include <highgui.h>
#include <math.h>
#else
#include <opencv/cv.h>
#include <opencv/highgui.h>
#include <math.h>
#endif
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>

#define _DEBUG 0

/* 処理するときの縦サイズ(px).
   小さいほうが速いけど、小さすぎると小さい線が見つからなくなる.
   cvHoughLines2のパラメータもこれをベースに決める.
*/
#define SCALE_SIZE 640.0f 

/* 最低オフセットが存在することを想定する(px).
   真ん中にある謎の黒い線の上下をtop,bottomに選択しないためのテキトウな処理で使う. */
#define HARD_OFFSET 32

/* ページ中心のズレの許容範囲(px / 2).
   余白を切った矩形の中心からこの距離範囲の間でページの中心を決める.
*/
#define CENTER_RANGE 64

/* 中心を決める際に使う線の最大数.
*/
#define CENTER_SAMPLE_MAX 1024

/* 中心決めるときのクラスタ数 */
#define CENTER_K 3

int 
float_cmp(const void *p1, const void *p2)
{
	if (*(const float *)p1 > *(const float *)p2) {
		return 1;
	} else if (*(const float *)p1 < *(const float *)p2) {
		return -1;
	}
	return 0;
}

/* imgに近デジの画像を渡すと左右のページの範囲を返す処理 */
int 
page_split(IplImage *img,
		   CvRect *left_page, CvRect *right_page)
{
	int i, j;
	IplImage *edges, *small_img;
	float scale;
	CvMemStorage *storage;
	CvSeq *lines = 0;
	int top, left, right, bottom,
		center, center_base, samples;
	CvMat *center_samples = cvCreateMat(CENTER_SAMPLE_MAX, 1, CV_32FC1);
	CvMat *labels = cvCreateMat(CENTER_SAMPLE_MAX, 1, CV_32SC1);

	if (img == NULL) {
		return -1;
	}

	/* リサイズしたエッジ画像から確率的ハフ変換で線を検出する */
	scale = SCALE_SIZE / img->height;
	small_img = cvCreateImage(
		cvSize((int)(img->width * scale),
		(int)(img->height * scale)), img->depth, img->nChannels);
	edges = cvCreateImage(cvGetSize(small_img), small_img->depth, 1);
	cvResize(img, small_img, 1);
	cvCvtColor(small_img, edges, CV_BGR2GRAY);
	cvCanny(edges, edges, 50, 200, 3);

	lines = 0;
	storage = cvCreateMemStorage(0);
	lines = cvHoughLines2(edges, storage,
		CV_HOUGH_PROBABILISTIC, 1, CV_PI / 2, 50, 32, 16);

	/* 余白を切る範囲を決める */
	top = INT_MAX;
	bottom = 0;
	left = INT_MAX;
	right = 0;
	for (i = 0; i < lines->total; i++) {
		CvPoint *points = (CvPoint *) cvGetSeqElem (lines, i);
		if (abs(points[0].x - points[1].x) > abs(points[0].y - points[1].y)) {
			/* 横線 */
			for (j = 0; j < 2; ++j) {
				if (top > points[j].y
					&& points[j].y > HARD_OFFSET) 
			  {
				  top = points[j].y;
				}
				if (bottom < points[j].y 
					&& points[j].y < img->height - HARD_OFFSET) 
				{
					bottom = points[j].y;
				}
			}
		} else {
			/* 縦線 */
			for (j = 0; j < 2; ++j) {
				if (left > points[j].x
					&& points[j].x > HARD_OFFSET)
				{
					left = points[j].x;
				}
				if (right < points[j].x
					&& points[j].x < img->width - HARD_OFFSET)
				{
					right = points[j].x;
				}
			}
		}
#if _DEBUG
		{	  /* 検出した線をimgに描く(debug用) */
			CvPoint tmp[2];
			tmp[0] = points[0];
			tmp[1] = points[1];
			tmp[0].x = (int)(points[0].x / scale);
			tmp[0].y = (int)(points[0].y / scale);
			tmp[1].x = (int)(points[1].x / scale);
			tmp[1].y = (int)(points[1].y / scale);
			cvLine(img, tmp[0], tmp[1], CV_RGB (255, 0, 0), 1, 8, 0);

			if (abs(points[0].x - points[1].x) > abs(points[0].y - points[1].y)) {
				cvLine(img, tmp[0], tmp[1], CV_RGB (0, 0, 255), 1, 8, 0);
			} else {
				cvLine(img, tmp[0], tmp[1], CV_RGB (0, 255, 0), 1, 8, 0);
			}
		}
#endif
	}

	/* 左右の分割点を決める */

	/* 中心あたりをサンプリング */

	center_base = left + (right - left) / 2;
	center = center_base;
	samples = 0;
	cvZero(center_samples);
	cvZero(labels);
	for (i = 0; i < lines->total; i++) {
		CvPoint *points = (CvPoint *)cvGetSeqElem(lines, i);
		if (abs(points[0].x - points[1].x) < abs(points[0].y - points[1].y)) 
		{
			/* 縦線 */
			for (j = 0; j < 2; ++j) {
				int dist = abs(points[j].x - center_base);
				if (dist < CENTER_RANGE) {
					CV_MAT_ELEM(*center_samples, float, samples, 0) = (float)points[j].x;
					if (++samples >= CENTER_SAMPLE_MAX) {
						goto _break;
					}
#if _DEBUG
					{	  /* サンプリングした線をimgに描く(debug用) */
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

	/* クラスタリングして中心を決める */
	if (samples > CENTER_K) {
		float label_centers[CENTER_K] = {0};
		int label_counts[CENTER_K] = {0};

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
			if (label_counts[i] > 0) {
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

/* テストテスト */
int
main (int argc, char **argv)
{
	int ret;
	IplImage *img = NULL;
	CvRect left_page, right_page;

	if (argc >= 2) {
		img = cvLoadImage(argv[1], CV_LOAD_IMAGE_COLOR);
	}
	if (img == NULL) {
		return -1;
	}

	/* ページの範囲を取得 */
	ret = page_split(img, &left_page, &right_page);
	if (ret != 0) {
		return -1;
	}

	/* 結果を表示してみる */
	cvRectangle(img,
		cvPoint(left_page.x, left_page.y),
		cvPoint(left_page.x + left_page.width, left_page.y + left_page.height),
		CV_RGB(255, 0, 0), 2, 8, 0);

	cvRectangle(img,
		cvPoint(right_page.x, right_page.y),
		cvPoint(right_page.x + right_page.width, right_page.y + right_page.height),
		CV_RGB(255, 0, 0), 2, 8, 0);

	cvNamedWindow ("kindai_crop", CV_WINDOW_AUTOSIZE);
	cvShowImage ("kindai_crop", img);
	cvWaitKey (0);

	cvDestroyWindow ("kindai_crop");
	cvReleaseImage (&img);

	return 0;
}
