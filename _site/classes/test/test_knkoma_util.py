# -*- coding: utf-8 -*-
import pytest
from hamcrest import *
from classes.knpage import KnPage
from classes.knpage import KnPageException

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


def pytest_funcarg__kn(request):
    img_fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
    params_fname = DATA_DIR + '/twletters_01.json'
    kn = KnPage(fname=img_fname, datadir=DATA_DIR, params=params_fname)
    return kn


def pytest_funcarg__kn2(request):
    fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
    params_file_name = DATA_DIR + '/twletters_01.json'
    return KnPage(fname, params=params_file_name)


class TestTmpDir:
    def test_write(self, kn, tmpdir):
        dataDirectory = tmpdir.mkdir('data')
        sampleFile = str(dataDirectory.join("sample.jpeg"))
        kn.write(sampleFile)
        assert 'sample.jpeg' in sampleFile

    def test_write_data_file(self, kn):
        kn.write_data_file(DATA_DIR)


class TestCompLine:
    @pytest.mark.parametrize("line0,line1,horv", [
        ([(4, 4), (8,  4)], [(1, 3), (7, 5)], 'h'),
        ([(4, 24), (8,  4)], [(0, 15), (0, 20)], 'h'),
        ([(10, 100), (20, 10)], [(100, 50), (1000, 5)], 'v'),
        ([(10, 1000), (50, 100)], [(7, 25), (35, 20)], 'v')
    ])
    def test_complLne_wrong_recognition(self, line0, line1, horv):
        img_fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
        params_fname = DATA_DIR + '/twletters_01.json'
        kn = KnPage(fname=img_fname, datadir=DATA_DIR, params=params_fname)
        with pytest.raises(KnPageException) as e:
            kn.compLine(line0, line1, horv)
            assert 'wrong recognition' in str(e)
            kn.compLine(line1, line0, horv)
            assert 'wrong recognition' in str(e)

    @pytest.mark.parametrize("line0, line1, horv", [
        ([(4, 4), (8,  4)], [(1, 3), (7, 3)], 'h'),
        ([(4, 4), (8,  4)], [(10, 0), (20, 0)], 'h'),
        ([(10, 10), (20, 10)], [(100, 5), (1000, 5)], 'h'),
        ([(10, 100), (50, 100)], [(7, 20), (35, 20)], 'h')
    ])
    def test_complLne_horizontal(self, line0, line1, horv):
        img_fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
        params_fname = DATA_DIR + '/twletters_01.json'
        kn = KnPage(fname=img_fname, datadir=DATA_DIR, params=params_fname)
        result = kn.compLine(line0, line1, horv)
        assert result == "upper"
        result = kn.compLine(line1, line0, horv)
        assert result == "lower"

    @pytest.mark.parametrize("line0, line1, horv", [
        ([(4, 4), (8,  4)], [(1, 3), (7, 3)], 'v'),
        ([(4, 4), (8,  4)], [(10, 0), (20, 0)], 'v'),
        ([(10, 10), (20, 10)], [(100, 5), (1000, 5)], 'v'),
        ([(10, 100), (50, 100)], [(7, 20), (35, 20)], 'v')
    ])
    def test_complLne_vertical(self, line0, line1, horv):
        img_fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
        params_fname = DATA_DIR + '/twletters_01.json'
        kn = KnPage(fname=img_fname, datadir=DATA_DIR, params=params_fname)
        tr = lambda tup: (tup[1], tup[0])
        result = kn.compLine(map(tr, line0), map(tr, line1), horv)
        assert result == "right"
        result = kn.compLine(map(tr, line1), map(tr, line0), horv)
        assert result == "left"


class TestInterSection:
    @pytest.mark.parametrize("line", [
        [(10, 10), (10, 3)],
        [(10, 10), (10, 7)],
        [(10, 10), (10, 8)],
        [(10, 10), (10, 53)]
    ])
    def test_isVertical_truth(self, line):
        img_fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
        params_fname = DATA_DIR + '/twletters_01.json'
        kn = KnPage(fname=img_fname, datadir=DATA_DIR, params=params_fname)
        result = kn.isVertical(line)
        assert result is True

    @pytest.mark.parametrize("line", [
        [(10, 10), (0, 3)],
        [(10, 10), (30, 7)],
        [(10, 10), (20, 8)],
        [(10, 10), (50, 53)]
    ])
    def test_isVertical_false(self, line):
        img_fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
        params_fname = DATA_DIR + '/twletters_01.json'
        kn = KnPage(fname=img_fname, datadir=DATA_DIR, params=params_fname)
        result = kn.isVertical(line)
        assert result is False

    @pytest.mark.parametrize("line", [
        [(10, 3), (100, 3)],
        [(10, 7), (30, 7)],
        [(10, 8), (20, 8)],
        [(10, 53), (50, 53)]
    ])
    def test_isHorizontal_truth(self, line):
        img_fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
        params_fname = DATA_DIR + '/twletters_01.json'
        kn = KnPage(fname=img_fname, datadir=DATA_DIR, params=params_fname)
        result = kn.isHorizontal(line)
        assert result is True

    @pytest.mark.parametrize("line", [
        [(10, 10), (0, 3)],
        [(10, 10), (30, 7)],
        [(10, 10), (20, 8)],
        [(10, 10), (50, 53)]
    ])
    def test_isHorizontal_false(self, line):
        img_fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
        params_fname = DATA_DIR + '/twletters_01.json'
        kn = KnPage(fname=img_fname, datadir=DATA_DIR, params=params_fname)
        result = kn.isHorizontal(line)
        assert result is False

    @pytest.mark.parametrize("line1, line2", [
        ([(10, 10), (0,  3)], [(10, 190), (0, 3)]),
        ([(10, 10), (30,  7)], [(10, 10), (0, 3)]),
        ([(10, 10), (20,  8)], [(10, 10), (0, 3)]),
        ([(10, 10), (50, 53)], [(20, 20), (5, 2)])
    ])
    def test_isHorizontal_false2(self, line1, line2):
        img_fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
        params_fname = DATA_DIR + '/twletters_01.json'
        kn = KnPage(fname=img_fname, datadir=DATA_DIR, params=params_fname)
        result = kn.getIntersection(line1, line2)
        assert result is not False

    @pytest.mark.parametrize("line1,line2", [
        ([(4, 2), ( 8,  4)], [(1, 3), (2, 6)]),
        ([(4, 2), ( 8,  4)], [(10, 10), (20, 20)]),
        ([(10, 10), (20, 20)], [(100, 10), (1000, 100)]),
        ([(10, 10), (50, 50)], [(7, 2), (35, 10)])
    ])
    def test_getIntersection(self, line1, line2):
        slide = lambda x,y,line:[(line[0][0]+x,line[0][1]+y),(line[1][0]+x,line[1][1]+y)]
        img_fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
        params_fname = DATA_DIR + '/twletters_01.json'
        kn = KnPage(fname=img_fname, datadir=DATA_DIR, params=params_fname)
        result = kn.getIntersection(line1, line2)
        assert result == (0, 0)
        l1 = slide(5,8,line1)
        l2 = slide(5,8,line2)
        result = kn.getIntersection(l1, l2)
        assert result == (5, 8)

    @pytest.mark.parametrize("line1,line2", [
        ([(4, 2), (4, 4)], [(10, 5), (8, 4)]),
        ([(4, 2), (4, 4)], [(5, 2), (8, 2)]),
        ([(4, 2), (4, 4)], [(0, 4), (8, 0)])
    ])
    def test_getIntersection_with_vertical(self, line1, line2):
        slide = lambda x, y, line : [(line[0][0] + x, line[0][1] + y), (line[1][0] + x, line[1][1] + y)]
        img_fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
        params_fname = DATA_DIR + '/twletters_01.json'
        kn = KnPage(fname=img_fname, datadir=DATA_DIR, params=params_fname)
        result = kn.getIntersection(line1, line2)
        assert result == (4, 2)
        l1 = slide(5, 8, line1)
        l2 = slide(5, 8, line2)
        result = kn.getIntersection(l1, l2)
        assert result == (9, 10)

