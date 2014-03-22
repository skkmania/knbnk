# -*- coding: utf-8 -*-
import pytest
import os.path
import json
import shutil

from classes.knpage import KnPage
from classes.knpage import KnPageException
from classes.knpage import KnPageParamsException

HOME_DIR = '/home/skkmania'
DATA_DIR = HOME_DIR + '/mnt2/workspace/pysrc/knbnk/data/1123003'

opts_template = {
        "scale_size": 640.0,
        "boundingRect": [ 16, 32 ],
        "imgfname": DATA_DIR + '/007.jpeg',
        "outfilename": "hough_1_180_200_007",
        "mode": "EXTERNAL",
        "canny": [ 50, 200, 3 ],
        "hough": [ 1, 180, 200 ],
        "paramfname": DATA_DIR + '/hough_1_180_200.json',
        "method": "NONE",
        "outdir": DATA_DIR
}

def generate_opts(opts_list, kvs_list, data_dir=DATA_DIR):
    """
    入力:
        opts_list : 既存のoptのlist
        kvs_list   : 適用したい{key： [values]}のlist
    戻り値:
        opt_listにkvs_listを反映させたもの。
        optのlist
        その長さは、len(opts_list) * len(kvs_list)となる
    使用例:
        opts_list = [{"a":10}, {"b":20}]
        kvs_list = [{"a":[10,20,30,40]}, {"b":[30,40,50,60]}]
        とすると戻り値は
        [{"a":10}, {"a":20}, {"a":30}, {"a":40},
         {"b":20}, {"b":30}, {"b":40}, {"b":50}, {"b":60}]
         となる。
         ココロとしては、既存のparameter fileに対して
             対象画像を一気に増やしたい
             cannyのparameterをいろいろと変えてみたい
         というときに使う
    """
    ret = []
    for kvs in kvs_list:
        key = kvs.keys()[0]
        values = kvs.values()[0]
        for opt in opts_list:
            for value in values:
                new_opt = opt.copy()
                if key in opt:
                    if opt[key] != value:
                        new_opt[key] = value
                        ret.append(new_opt)
                else:
                    new_opt[key] = value
                    ret.append(new_opt)
    return ret

class TestGenerateOpts:
    def test_generate_opts(self, tmpdir):
        result = generate_opts(opts_list=[{"a":10}, {"b":20}],
                               kvs_list=[{"a":[10,20,30,40]}, {"b":[30,40,50,60]}])
        assert {"a":20} in result
        dataDirectory = tmpdir.mkdir('data')
        sampleFile = dataDirectory.join("result.txt")
        with open(str(sampleFile), 'w') as f:
            f.write(str(result))

    def test_generate_opts2(self, tmpdir):
        result = generate_opts(opts_list=[{"a":10, "b":20}],
                               kvs_list=[{"a":[10,20,30,40]}, {"b":[30,40,50,60]}])
        assert {"a":20, "b":20} in result
        dataDirectory = tmpdir.mkdir('data')
        sampleFile = dataDirectory.join("result2.txt")
        with open(str(sampleFile), 'w') as f:
            f.write(str(result))

def edit_parms_file(pfbody=None, imfname=None, opts=None):
    if imfname:
        img_fname = DATA_DIR + '/' + imfname
    if pfbody:
        pfname = DATA_DIR + '/%s.json' % pfbody
        with open(pfname) as f:
            lines = f.readlines()
            params = json.loads(''.join(lines))
        params['imgfname'] = img_fname
        params['outfilename'] = DATA_DIR + '/' + pfbody + '_' + imfname.split('.')[0]
        shutil.move(pfname, pfname + '.bak')
    else:
        params = {}

    if opts:
        for k in opts:
            params[k] = opts[k]

    with open(params["paramfname"], "w") as f:
        json.dump(params, f, sort_keys=False, indent=4)


def pytest_funcarg__kn(request):
    #img_fname = '/home/skkmania/workspace/pysrc/knbnk/data/1123003/007.jpeg'
    img_fname = DATA_DIR + '/007.jpeg'
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


class TestWriteSmallImage:
    def test_write_small_img(self):
        opts = {
                "scale_size": 640.0,
                "boundingRect": [ 16, 32 ],
                "imgfname": "/home/skkmania/mnt2/workspace/pysrc/knbnk/data/1123003/007.jpeg",
                "outfilename": "/home/skkmania/mnt2/workspace/pysrc/knbnk/data/1123003/hough_1_180_200_007",
                "mode": "EXTERNAL",
                "canny": [ 50, 200, 3 ],
                "hough": [ 1, 180, 200 ],
                "paramfname": "/home/skkmania/mnt2/workspace/pysrc/knbnk/data/1123003/hough_1_180_200.json",
                "method": "NONE",
                "outdir": "/home/skkmania/mnt2/workspace/pysrc/knbnk/data/1123003"
        }
        edit_parms_file(opts=opts)
        kn = KnPage(params=opts["paramfname"])
        kn.prepareForLines()
        kn.write_small_img(DATA_DIR)
        assert kn.small_img is not None


class TestSmallImage:
    def test_get_small_img_with_lines(self, kn):
        kn.prepareForLines()
        kn.getHoughLines()
        kn.get_small_img_with_lines()
        assert kn.small_img is not None

    def test_write_small_img(self):
        img_fname = DATA_DIR + '/007.jpeg'
        params_fname = DATA_DIR + '/005_split_01.json'
        edit_parms_file(pfbody, imfname, opts=None)
        kn = KnPage(fname=img_fname, datadir=DATA_DIR, params=params_fname)
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


class TestGetHoughLinesWithManyPatterns:
    @pytest.mark.parametrize("pfbody,imfname", [
        ("hough_1_2_100", "007.jpeg"),
        ("hough_1_2_150", "007.jpeg"),
        ("hough_1_180_100", "007.jpeg"),
        ("hough_1_180_150", "007.jpeg"),
        ("hough_1_180_200", "007.jpeg"),
        ("hough_1_90_150", "007.jpeg"),
        ("hough_1_90_200", "007.jpeg")])
    def test_get_small_img_with_linesP(self, pfbody, imfname):
        edit_parms_file(pfbody, imfname)
        params_fname = DATA_DIR + '/%s.json' % pfbody
        kn = KnPage(params=params_fname)
        kn.prepareForLines()
        kn.getHoughLines()
        kn.get_small_img_with_lines()
        kn.write_small_img_with_lines(DATA_DIR)
        assert kn.small_img_with_lines is not None


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


