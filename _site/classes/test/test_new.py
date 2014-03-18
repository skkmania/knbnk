# -*- coding: utf-8 -*-
import pytest
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


class TestParams:
    def pytest_funcarg__kn(request):
        fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
        return KnPage(fname, datadir=DATA_DIR)

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
        assert len(kn.parameters) == 5
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


class TestTmpDir:
    @pytest.fixture
    def test_write(self, kn, tmpdir):
        dataDirectory = tmpdir.mkdir('data')
        sampleFile = dataDirectory.join("sample.jpeg")
        kn.write(sampleFile)
        assert sampleFile == '/tmp/data/sample.jpe'


class TestContours:
    def test_getContours(self, kn):
        kn.getContours()
        assert kn.gray is not None
        assert kn.contours is not None
        assert kn.hierarchy is not None

#class TestSeparate:
#    def test_separate(self, kn):
#        kn.getCentroids()
#        arr = kn.centroids
#        x = range(1, len(arr))
#        actual = kn.separate(arr, x)
#        assert len(actual) > 0
