# -*- coding: utf-8 -*-
from classes.knpage import KnPage

DATA_DIR = '/home/skkmania/mnt2/workspace/pysrc/knbnk/data'


def pytest_funcarg__myfuncarg(request):
        return 42


def test_function(myfuncarg):
        assert myfuncarg == 42


def pytest_funcarg__kn(request):
    fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
    return KnPage(fname, datadir=DATA_DIR)


def pytest_funcarg__kn2(request):
    fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
    params_file_name = DATA_DIR + '/twletters_01.json'
    return KnPage(fname, params=params_file_name)


class TestBinarized:
    def test_write_binarized_file(self, kn):
        kn.write_binarized_file(DATA_DIR)

class TestContours:
    def test_getContours(self, kn):
        kn.getContours()
        assert kn.gray is not None
        assert kn.contours is not None
        assert kn.hierarchy is not None

    def test_getCentroids(self, kn):
        kn.getCentroids()
        assert kn.centroids is not None

    def test_writeContour(self, kn):
        kn.getContours()
        kn.writeContour()
        assert kn.img_of_contours is not None

    def test_write_original_with_contour_file(self, kn):
        kn.write_original_with_contour_file(DATA_DIR)

    def test_write_original_with_contour_and_rect_file(self, kn):
        kn.write_original_with_contour_and_rect_file(DATA_DIR)


class TestWriteAll:
    def test_write_all(self):
        fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
        for i in range(2,9):
          params_file_name = DATA_DIR + '/twletters_0' + str(i) + '.json'
          kn = KnPage(fname, datadir=DATA_DIR, params=params_file_name)
          kn.write_all(DATA_DIR)

