# -*- coding: utf-8 -*-
import pytest
from classes.knpage import KnPage
from classes.knpage import KnPageException
from classes.knpage import KnPageParamsException

HOME_DIR = '/home/skkmania'
DATA_DIR = HOME_DIR + '/mnt2/workspace/pysrc/knbnk/data'


def pytest_funcarg__kn(request):
    img_fname = '/home/skkmania/workspace/pysrc/knbnk/data/005.jpeg'
    params_fname = DATA_DIR + '/005_split_01.json'
    kn = KnPage(fname=img_fname, datadir=DATA_DIR, params=params_fname)
    return kn


def pytest_funcarg__kn2(request):
    fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
    params_file_name = DATA_DIR + '/twletters_01.json'
    return KnPage(fname, params=params_file_name)


class TestGetHoughLinesP:
    def test_getHoughLinesP(self, kn):
        kn.prepareForLines()
        kn.getHoughLinesP()

    def test_write_lines_to_file(self, kn):
        kn.prepareForLines()
        kn.getHoughLinesP()
        kn.write_linesP_to_file(DATA_DIR)


class TestGetHoughLines:
    def test_prepareForLines(self, kn):
        kn.prepareForLines()

    def test_getHoughLines(self, kn):
        kn.prepareForLines()
        kn.getHoughLines()

    def test_write_lines_to_file(self, kn):
        kn.prepareForLines()
        kn.getHoughLines()
        kn.write_lines_to_file(DATA_DIR)
        assert len(kn.lines) > 0


class TestSmallImage:
    def test_get_small_img_with_lines(self, kn):
        kn.prepareForLines()
        kn.getHoughLines()
        kn.get_small_img_with_lines()
        assert kn.small_img is not None

    def test_write_small_img(self, kn):
        kn.prepareForLines()
        kn.getHoughLines()
        kn.write_small_img(DATA_DIR)
        assert kn.small_img is not None

    def test_write_small_img_with_lines(self, kn):
        kn.prepareForLines()
        kn.getHoughLines()
        kn.get_small_img_with_lines()
        kn.write_small_img_with_lines(DATA_DIR)
        assert kn.small_img is not None


class TestSmallImageP:
    def test_get_small_img_with_linesP(self, kn):
        kn.prepareForLines()
        kn.getHoughLinesP()
        kn.get_small_img_with_linesP()
        kn.write_small_img_with_linesP(DATA_DIR)
        assert kn.small_img_with_linesP is not None


class TestParams:
    def pytest_funcarg__kn(request):
        fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
        paramfname = DATA_DIR + '/twletters_01.json'
        return KnPage(fname, datadir=DATA_DIR, params=paramfname)

    def pytest_funcarg__kn2(request):
        fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
        params_file_name = DATA_DIR + '/twletters_01.json'
        return KnPage(fname, params=params_file_name)

    def test_read_params(self, kn):
        """
          "outfilename"  : "twl_can_50_200",
          "boundingRect" : [16, 32],
          "mode"         : "EXTERNAL",
          "method"       : "NONE",
          "canny"        : [50, 200]
        """
        params = DATA_DIR + '/twletters_01.json'
        kn.read_params(params)
        assert kn.parameters is not None
        assert len(kn.parameters) == 8
        assert kn.parameters['outfilename'] == "twl_can_50_200"
        assert kn.parameters['boundingRect'] == [16, 32]
        assert kn.parameters['mode'] == "EXTERNAL"
        assert kn.parameters['method'] == "NONE"
        assert kn.parameters['canny'] == [50, 200]

    def test_new_with_params(self, kn2):
        assert kn2.img is not None
        assert kn2.img.shape != (100, 100, 3)
        assert kn2.img.shape == (558, 669, 3)
        assert kn2.height == 558
        #assertEqual(kn2.width, 669)
        #assertEqual(kn2.depth, 3)

    def test_divide(self, kn):
        kn.divide()
        assert kn.left == kn.right

    def test_write(self, kn):
        #dataDirectory = tmpdir.mkdir('data')
        #sampleFile = dataDirectory.join("sample.jpeg")
        #kn.write(sampleFile)
        kn.write("/tmp/outfile.jpeg")

    def test_write_with_params(self, kn2):
        kn2.write_data_file(DATA_DIR)
        kn2.write_binarized_file(DATA_DIR)
        kn2.write_contours_bounding_rect_to_file(DATA_DIR)


class TestTmpDir:
    @pytest.fixture
    def test_write(self, kn, tmpdir):
        dataDirectory = tmpdir.mkdir('data')
        sampleFile = dataDirectory.join("sample.jpeg")
        kn.write(sampleFile)
        assert sampleFile == '/tmp/data/sample.jpe'


class TestFileName:
    def test_mkFilename(self, kn):
        name = kn.mkFilename('_cont')
        expect = DATA_DIR + '/twl_can_50_200_cont.jpg'
        assert name == expect

    def test_write_data_file(self, kn):
        kn.write_data_file(DATA_DIR)


class TestBoundingRect:
    def test_write_contours_bounding_rect_to_file(self, kn):
        kn.write_contours_bounding_rect_to_file(DATA_DIR)

    def test_get_boundingBox(self, kn):
        outer_box = kn.get_boundingBox([box01, box02, box03])
        assert outer_box == (20, 30, 25, 25)
        outer_box = kn.get_boundingBox([box01, box02, box03, box04, box05])
        assert outer_box == (10, 20, 45, 45)

    def test_include(self, kn):
        assert not kn.include(box01, box02)
        assert not kn.include(box01, box03)
        assert not kn.include(box01, box04)
        assert kn.include(box02, box06)

    def test_intersect(self):
        box01 = (20, 30, 10, 10)
        box02 = (25, 35, 15, 15)
        box03 = (35, 45, 10, 10)
        box04 = (35, 20, 20, 20)
        box05 = (10, 45, 20, 20)
        fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
        params_fname = DATA_DIR + '/twletters_01.json'
        kn = KnPage(fname=fname, datadir=DATA_DIR, params=params_fname)
        assert kn.intersect(box01, box02)
        assert kn.intersect(box01, box03)
        assert not kn.intersect(box01, box03, 0, 0)
        assert kn.intersect(box01, box03)
        assert kn.intersect(box01, box04)
        assert not kn.intersect(box01, box04, 0, 0)
        assert kn.intersect(box01, box05)
        assert not kn.intersect(box01, box05, 0, 0)
        assert kn.intersect(box02, box03)
        assert kn.intersect(box02, box04)
        assert kn.intersect(box02, box05)
        assert kn.intersect(box03, box04)
        assert not kn.intersect(box03, box04, 0, 0)
        assert kn.intersect(box03, box05)
        assert not kn.intersect(box03, box05, 0, 0)
        assert kn.intersect(box04, box05)
        assert not kn.intersect(box04, box05, 0, 0)

    def test_sweep_included_boxes(self, kn):
        result = kn.sweep_included_boxes([box01, box02, box03, box04, box05, box06])
        assert len(result) == 5

    def test_sweep_included_boxes_2(self, kn):
        kn.sweep_included_boxes()
        kn.write_boxes_to_file(DATA_DIR)


