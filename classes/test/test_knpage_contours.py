# -*- coding: utf-8 -*-
import pytest
from classes.knpage import *
from classes.knutil import *

DATA_DIR = '/home/skkmania/mnt2/workspace/pysrc/knbnk/data'


class TestBinarized:
    def test_write_binarized_file(self, kn005):
        kn005.write_binarized_file(DATA_DIR)


class TestContours:
    def test_getContours(self, twl):
        twl.getContours()
        assert twl.gray is not None
        assert twl.contours is not None
        assert twl.hierarchy is not None

    def test_getCentroids(self, twl):
        twl.getCentroids()
        assert twl.centroids is not None

    def test_writeContour(self, twl):
        twl.getContours()
        twl.writeContour()
        assert twl.img_of_contours is not None

    def test_write_original_with_contour_file(self, twl):
        twl.write_original_with_contour_file()

    def test_write_original_with_contour_and_rect_file(self, twl):
        twl.write_original_with_contour_and_rect_file()


class TestWriteBinarized:
    def test_write_binarized_file(self, kn005):
        kn005.write_binarized_file()


class TestWriteContoursBoundingRect:
    def test_write_contours_bounding_rect_to_file(self, kn005):
        kn005.write_contours_bounding_rect_to_file()


class TestCollectedBoxes:
    """
    注意!：対象がオリジナルのひとコマなため10分程度かかる
    """
    def test_collect_boxes(self, kn005):
        kn005.collect_boxes()
        kn005.write_collected_boxes_to_file()
        kn005.write_original_with_collected_boxes_to_file()


class TestWriteAll:
    """
    注意!：対象がオリジナルのひとコマなため15分程度かかる
    """
    def test_write_all(self, kn005):
        kn005.write_all(DATA_DIR)


class TestWriteAllForAllParams:
    def test_write_all(self):
        fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
        for i in range(2, 9):
            params_file_name = DATA_DIR + '/twletters_0' + str(i) + '.json'
            kn = KnPage(fname, datadir=DATA_DIR, params=params_file_name)
            kn.write_all(DATA_DIR)


class TestWriteGradients:
    @pytest.mark.parametrize("sobel", [
        [6, 1, 0, 5],
        [6, 1, 1, 5],
        [6, 0, 1, 5]
    ])
    def test_write_gradients(self, sobel):
        bookId = 'twletters'
        params = {
            "scale_size":   640.0,
            "imgfname":     "/".join([DATA_DIR, bookId, "twletters.jpg"]),
            "outdir":       "/".join([DATA_DIR, bookId]),
            "paramfname":   "/".join([DATA_DIR, bookId, "twl_sobel.json"]),
            "outfilename":  "auto",
            "boundingRect": [16, 32],
            "mode":         "TREE",
            "method":       "NONE",
            "sobel":        sobel,
            "scharr":       [-1, 0, 1]
        }
        print_params_files([params])
        check_test_environment(params, bookId)
        knSobel = KnPage(params=params['paramfname'])
        knSobel.getGradients()
        knSobel.write_gradients()


class TestWriteScharr:
    @pytest.mark.parametrize("scharr", [
        [-1, 0, 1],
        [-1, 1, 0]
    ])
    def test_write_gradients(self, scharr):
        bookId = 'twletters'
        params = {
            "scale_size":   640.0,
            "imgfname":     "/".join([DATA_DIR, bookId, "twletters.jpg"]),
            "outdir":       "/".join([DATA_DIR, bookId]),
            "paramfname":   "/".join([DATA_DIR, bookId, "twl_scharr.json"]),
            "outfilename":  "auto",
            "boundingRect": [16, 32],
            "mode":         "TREE",
            "method":       "NONE",
            "scharr":       scharr
        }
        print_params_files([params])
        check_test_environment(params, bookId)
        knSobel = KnPage(params=params['paramfname'])
        knSobel.getGradients()
        knSobel.write_gradients()


#class TestProcessParamFiles:
#    def test_readfiles(self):
#        sampleDirName = DATA_DIR
#        for f in dir:
#            outdir = OUT_DIR + f
#            kn = KnPage(params=f, outdir=outdir)
