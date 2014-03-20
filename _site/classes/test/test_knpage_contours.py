# -*- coding: utf-8 -*-
from classes.knpage import KnPage

DATA_DIR = '/home/skkmania/mnt2/workspace/pysrc/knbnk/data'


def pytest_funcarg__kn(request):
    img_fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
    params_fname = DATA_DIR + '/twletters_01.json'
    kn = KnPage(fname=img_fname, datadir=DATA_DIR, params=params_fname)
    return kn


def pytest_funcarg__kn2(request):
    fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
    params_file_name = DATA_DIR + '/twletters_01.json'
    return KnPage(fname, params=params_file_name)


def pytest_funcarg__knSobel1(request):
    fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
    params_file_name = DATA_DIR + '/twletters_sobel_1.json'
    return KnPage(fname=fname, datadir=DATA_DIR, params=params_file_name)


def pytest_funcarg__knSobel2(request):
    fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
    params_file_name = DATA_DIR + '/twletters_sobel_2.json'
    return KnPage(fname=fname, datadir=DATA_DIR, params=params_file_name)


def pytest_funcarg__knSobel3(request):
    fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
    params_file_name = DATA_DIR + '/twletters_sobel_3.json'
    return KnPage(fname=fname, datadir=DATA_DIR, params=params_file_name)


def pytest_funcarg__knScharr1(request):
    fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
    params_file_name = DATA_DIR + '/twletters_scharr_1.json'
    return KnPage(fname=fname, datadir=DATA_DIR, params=params_file_name)


def pytest_funcarg__knScharr2(request):
    fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
    params_file_name = DATA_DIR + '/twletters_scharr_2.json'
    return KnPage(fname=fname, datadir=DATA_DIR, params=params_file_name)


def pytest_funcarg__knScharr3(request):
    fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
    params_file_name = DATA_DIR + '/twletters_scharr_3.json'
    return KnPage(fname=fname, datadir=DATA_DIR, params=params_file_name)


def pytest_funcarg__kn005(request):
    fname = DATA_DIR + '/005.jpeg'
    params_file_name = DATA_DIR + '/twletters_04.json'
    return KnPage(fname, datadir=DATA_DIR, params=params_file_name)


class TestBinarized:
    def test_write_binarized_file(self, kn005):
        kn005.write_binarized_file(DATA_DIR)


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
    def test_write_all(self, kn005):
        kn005.write_all(DATA_DIR)


class TestWriteAllForAllParams:
    def test_write_all(self):
        fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
        for i in range(2, 9):
            params_file_name = DATA_DIR + '/twletters_0' + str(i) + '.json'
            kn = KnPage(fname, datadir=DATA_DIR, params=params_file_name)
            kn.write_all(DATA_DIR)


class TestWriteSobel:
    def test_write_binarized_file1(self, knSobel1):
        outfilename = DATA_DIR + knSobel1.mkFilename('', '/')
        assert len(outfilename) > 0
        knSobel1.getBinarized()
        knSobel1.write(outfilename, knSobel1.binarized)

    def test_write_binarized_file2(self, knSobel2):
        outfilename = DATA_DIR + knSobel2.mkFilename('', '/')
        assert len(outfilename) > 0
        knSobel2.getBinarized()
        knSobel2.write(outfilename, knSobel2.binarized)

    def test_write_binarized_file3(self, knSobel3):
        outfilename = DATA_DIR + knSobel3.mkFilename('', '/')
        assert len(outfilename) > 0
        knSobel3.getBinarized()
        knSobel3.write(outfilename, knSobel3.binarized)


class TestWriteScharr:
    def test_write_binarized_file1(self, knScharr1):
        outfilename = DATA_DIR + knScharr1.mkFilename('', '/')
        assert len(outfilename) > 0
        knScharr1.getBinarized()
        knScharr1.write(outfilename, knScharr1.binarized)

    def test_write_binarized_file2(self, knScharr2):
        outfilename = DATA_DIR + knScharr2.mkFilename('', '/')
        assert len(outfilename) > 0
        knScharr2.getBinarized()
        knScharr2.write(outfilename, knScharr2.binarized)

#    def test_write_binarized_file3(self, knScharr3):
#        outfilename = DATA_DIR + knScharr3.mkFilename('', '/')
#        assert len(outfilename) > 0
#        knScharr3.getBinarized()
#        knScharr3.write(outfilename, knScharr3.binarized)


class TestProcessParamFiles:
    def test_readfiles(self):
        sampleDirName = DATA_DIR
        for f in dir:
            outdir = OUT_DIR + f
            kn = KnPage(params=f, outdir=outdir)

