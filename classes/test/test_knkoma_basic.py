# -*- coding: utf-8 -*-
import pytest
import hamcrest as h
from classes.knkoma import *
import classes.knutil as ku

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
    img_fname = DATA_DIR + '/twletters/001.jpg'
    params_fname = DATA_DIR + '/twletters/twletters_01.json'
    kn = KnKoma(fname=img_fname, datadir=DATA_DIR, params=params_fname)
    return kn


def pytest_funcarg__kn2(request):
    fname = DATA_DIR + '/twletters/twletters.jpg'
    params_file_name = DATA_DIR + '/twletters/twletters_01.json'
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
        with pytest.raises(ku.KnUtilParamsException) as e:
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
        h.assert_that(kn.height, h.equal_to(558))


class TestParams:
    def pytest_funcarg__kn(request):
        fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
        paramfname = DATA_DIR + '/twletters/twletters_01.json'
        return KnKoma(fname, datadir=DATA_DIR, params=paramfname)

    def pytest_funcarg__kn2(request):
        fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
        params_file_name = DATA_DIR + '/twletters/twletters_01.json'
        return KnKoma(fname, params=params_file_name)

    def test_read_params(self, kn):
        """
          "outfilename"  : "twl_can_50_200",
          "boundingRect" : [16, 32],
          "mode"         : "EXTERNAL",
          "method"       : "NONE",
          "canny"        : [50, 200]
        """
        params = DATA_DIR + '/twletters/twletters_01.json'
        ku.read_params(kn, params)
        assert kn.parameters is not None
        assert len(kn.parameters) == 12
        assert kn.parameters['outfilename'] == "twl_can_50_200_hough_1_2_100"
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


class TestTmpDir:
    def test_write(self, kn, tmpdir):
        dataDirectory = tmpdir.mkdir('data')
        sampleFile = str(dataDirectory.join("sample.jpeg"))
        kn.write(sampleFile)
        assert 'sample.jpeg' in sampleFile


class TestGradients:
    @pytest.mark.parametrize("idx", [1, 2, 3])
    def test_write(elf, idx):
        data_dir = DATA_DIR + '/twletters'
        fname = data_dir + '/twletters.jpg'
        paramfname = data_dir + '/twletters_gradients_0' + str(idx) + '.json'
        kn = KnKoma(fname, datadir=data_dir, params=paramfname)
        kn.getGradients()
        kn.write_gradients(data_dir)

    @pytest.mark.parametrize("idx", [1, 3, 5, 7])
    def test_write_sobel(elf, idx):
        data_dir = DATA_DIR + '/twletters'
        fname = data_dir + '/twletters.jpg'
        paramfname = data_dir + '/twletters_sobel_k_' + str(idx) + '.json'
        kn = KnKoma(fname, datadir=data_dir, params=paramfname)
        kn.getGradients()
        kn.write_gradients(data_dir)


class TestFileName:
    def test_mkFilename(self, kn):
        data_dir = DATA_DIR + '/twletters'
        name = ku.mkFilename(kn, '_cont')
        expect = data_dir + '/twl_can_50_200_hough_1_2_100_cont.jpg'
        assert name == expect

    def test_write_data_file(self, kn):
        kn.write_data_file(DATA_DIR)
