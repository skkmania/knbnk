# -*- coding: utf-8 -*-
import pytest
from hamcrest import *
from classes.knkoma import KnKoma
from classes.knkoma import KnKomaException
from classes.knkoma import KnKomaParamsException

HOME_DIR = '/home/skkmania'
DATA_DIR = HOME_DIR + '/mnt2/workspace/pysrc/knbnk/data'
box01 = (20, 30, 10, 10)
box02 = (25, 35, 15, 15)
box03 = (35, 45, 10, 10)
box04 = (35, 20, 20, 20)
box05 = (10, 45, 20, 20)
box06 = (27, 37, 10, 10)
box11 = (120, 30, 10, 10)
box12 = (125, 35, 15, 15)
box13 = (135, 45, 10, 10)
box14 = (135, 20, 20, 20)
box15 = (110, 45, 20, 20)
box16 = (127, 37, 10, 10)


def pytest_funcarg__myfuncarg(request):
        return 42


def test_function(myfuncarg):
        assert myfuncarg == 42


def pytest_funcarg__kn(request):
    img_fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
    params_fname = DATA_DIR + '/twletters_01.json'
    kn = KnKoma(fname=img_fname, datadir=DATA_DIR, params=params_fname)
    return kn


def pytest_funcarg__kn2(request):
    fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
    params_file_name = DATA_DIR + '/twletters_01.json'
    return KnKoma(fname, params=params_file_name)


class TestNew:
    def test_initialize_without_params(self):
        with pytest.raises(KnKomaException) as e:
            KnKoma()
        assert 'params is None' in str(e)

    def test_initialize_with_fname_not_existed(self):
        with pytest.raises(KnKomaParamsException) as e:
        #with pytest.raises(KnKomaException) as e:
            KnKoma(params='not_exist_file')
        assert 'not_exist_file' in str(e)

    def test_initialize_with_imcomplete_param_file(self):
        with pytest.raises(KnKomaParamsException) as e:
            KnKoma(params=DATA_DIR + '/imcomplete_sample.json')
        assert 'must be' in str(e)

    def test_new(self, kn):
        assert kn.img is not None
        assert kn.img.shape != (100, 100, 3)
        assert kn.img.shape == (558, 669, 3)
        assert kn.height == 558
        assert kn.width == 669
        assert kn.depth == 3
        assert kn.gray is not None
        assert kn.binarized is not None

    def test_new_try_hamcrest(self, kn):
        assert_that(kn.height, equal_to(558))

class TestParams:
    def pytest_funcarg__kn(request):
        fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
        paramfname = DATA_DIR + '/twletters_01.json'
        return KnKoma(fname, datadir=DATA_DIR, params=paramfname)

    def pytest_funcarg__kn2(request):
        fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
        params_file_name = DATA_DIR + '/twletters_01.json'
        return KnKoma(fname, params=params_file_name)

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
        assert len(kn.parameters) == 10
        assert kn.parameters['outfilename'] == "twl_can_50_200"
        assert kn.parameters['boundingRect'] == [16, 32]
        assert kn.parameters['mode'] == "EXTERNAL"
        assert kn.parameters['method'] == "NONE"
        assert kn.parameters['canny'] == [50, 200, 3]

    def test_new_with_params(self, kn2):
        assert kn2.img is not None
        assert kn2.img.shape != (100, 100, 3)
        assert kn2.img.shape == (558, 669, 3)
        assert kn2.height == 558
        #assertEqual(kn2.width, 669)
        #assertEqual(kn2.depth, 3)


    def test_write(self, kn, tmpdir):
        dataDirectory = tmpdir.mkdir('data')
        sampleFile = dataDirectory.join("sample.jpeg")
        kn.write(str(sampleFile))
        kn.write("/tmp/outfile.jpeg")

    def test_write_with_params(self, kn2):
        kn2.write_data_file(DATA_DIR)
        kn2.write_binarized_file(DATA_DIR)
        kn2.write_contours_bounding_rect_to_file(DATA_DIR)


class TestTmpDir:
    def test_write(self, kn, tmpdir):
        dataDirectory = tmpdir.mkdir('data')
        sampleFile = str(dataDirectory.join("sample.jpeg"))
        kn.write(sampleFile)
        assert 'sample.jpeg' in sampleFile


class TestGradients:
    @pytest.mark.parametrize("idx", [1, 2, 3])
    def test_write(elf, idx):
        fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
        paramfname = DATA_DIR + '/twletters_gradients_0' + str(idx) + '.json'
        kn = KnKoma(fname, datadir=DATA_DIR, params=paramfname)
        kn.getGradients()
        kn.write_gradients(DATA_DIR)

    @pytest.mark.parametrize("idx", [1, 3, 5, 7])
    def test_write_sobel(elf, idx):
        fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
        paramfname = DATA_DIR + '/twletters_sobel_k_' + str(idx) + '.json'
        kn = KnKoma(fname, datadir=DATA_DIR, params=paramfname)
        kn.getGradients()
        kn.write_gradients(DATA_DIR)

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
        kn = KnKoma(fname=fname, datadir=DATA_DIR, params=params_fname)
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


class TestManipulateBoxes:
    def test_get_adj_boxes(self, kn):
        boxes = [box01,box02,box03,box04,box05,box06, box11,box12,box13,box14,box15,box16]
        result = kn.get_adj_boxes(boxes, box01)
        assert list( set(result) - set([box01,box02,box03,box04,box05,box06]) )  == []

    def test_write_original_with_contour_and_rect_file(self, kn):
        kn.write_original_with_collected_boxes_to_file(DATA_DIR)

    def test_write_boxes_to_file(self, kn):
        kn.getCentroids()
        kn.write_boxes_to_file(DATA_DIR)

    def test_collect_boxes(self, kn):
        kn.collect_boxes()
        kn.write_collected_boxes_to_file(DATA_DIR)
        kn.write_original_with_collected_boxes_to_file(DATA_DIR)

#class TestSeparate:
#    def test_separate(self, kn):
#        kn.getCentroids()
#        arr = kn.centroids
#        x = range(1, len(arr))
#        actual = kn.separate(arr, x)
#        assert len(actual) > 0
