# -*- coding: utf-8 -*-
import pytest
import os.path
import json
import shutil
import itertools

from classes.knkoma import KnKoma

HOME_DIR = '/home/skkmania'
#DATA_DIR = HOME_DIR + '/mnt2/workspace/pysrc/knbnk/data/1123003'
#DATA_DIR = HOME_DIR + '/mnt2/workspace/pysrc/knbnk/data/1080614'
DATA_DIR = HOME_DIR + '/mnt2/workspace/pysrc/knbnk/data/1142178'
SRC_SAMPLE = {
    "scale_size": [640.0, 480.0, 320.0],
    "boundingRect": [[16, 32]],
    "imgfname": [DATA_DIR + '/007.jpeg', DATA_DIR + '/008.jpeg'],
    "mode": ["EXTERNAL"],
    "canny": [[50, 200, 3]],
    "hough": [[1, 180, 200]],
    "method": ["NONE"],
    "outdir": [DATA_DIR]
}

opts_template = {
    "scale_size": 640.0,
    "boundingRect": [16, 32],
    "imgfname": DATA_DIR + '/007.jpeg',
    "outfilename": "hough_1_180_200_007",
    "mode": "EXTERNAL",
    "canny": [50, 200, 3],
    "hough": [1, 180, 200],
    "paramfname": DATA_DIR + '/hough_1_180_200.json',
    "method": "NONE",
    "outdir": DATA_DIR
}


def mkoutfilename(params, fix):
    res = 'o_' + os.path.basename(params['imgfname']).split('.')[0]
    keys = params.keys()
    if 'scale_size' in keys:
        res += "_ss_" + str(int(params['scale_size']))

    if 'hough' in keys:
        res += "_hgh_" + "_".join(map(str, params['hough']))

    if 'canny' in keys:
        res += "_can_" + "_".join(map(str, params['canny']))

    return res + fix


def params_generator(source):
    keys = source.keys()
    vals_products = map(list, itertools.product(*source.values()))
    todict = lambda a, b: dict(zip(a, b))
    metadict = lambda a: (lambda b: todict(a, b))
    temp = map(metadict(keys), vals_products)
    cnt = 0
    for params in temp:
        params["outfilename"] = mkoutfilename(params, '_' + str(cnt))
        cnt += 1
        params["paramfname"] = params['outdir'] + '/' +\
            params['outfilename'] + '.json'
    return temp


def print_params_files(params_list):
    ret = []
    for params in params_list:
        fname = params['paramfname']
        with open(fname, 'w') as f:
            json.dump(params, f, sort_keys=False, indent=4)
            ret.append(fname)
    return ret


class TestParamsGenerator:
    def test_params_generator(self, tmpdir):
        src = SRC_SAMPLE
        result = params_generator(src)
        wrap = lambda d: d.get("scale_size")
        assert set(map(wrap, result)) == set(src["scale_size"])
        dataDirectory = tmpdir.mkdir('data')
        sampleFile = dataDirectory.join("result.txt")
        with open(str(sampleFile), 'w') as f:
            f.write(str(result))
        print_params_files(result)


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
        result = generate_opts(opts_list=[{"a": 10}, {"b": 20}],
                               kvs_list=[{"a": [10, 20, 30, 40]},
                                         {"b": [30, 40, 50, 60]}])
        assert {"a": 20} in result
        dataDirectory = tmpdir.mkdir('data')
        sampleFile = dataDirectory.join("result.txt")
        with open(str(sampleFile), 'w') as f:
            f.write(str(result))

    def test_generate_opts2(self, tmpdir):
        result = generate_opts(opts_list=[{"a": 10, "b": 20}],
                               kvs_list=[{"a": [10, 20, 30, 40]},
                                         {"b": [30, 40, 50, 60]}])
        assert {"a": 20, "b": 20} in result
        dataDirectory = tmpdir.mkdir('data')
        sampleFile = dataDirectory.join("result2.txt")
        with open(str(sampleFile), 'w') as f:
            f.write(str(result))


def edit_parms_file(pfbody=None, imfname=None, opts=None, data_dir=None):
    if data_dir:
        DATA_DIR = data_dir
    if imfname:
        img_fname = DATA_DIR + '/' + imfname
    if pfbody:
        pfname = DATA_DIR + '/%s.json' % pfbody
        with open(pfname) as f:
            lines = f.readlines()
            params = json.loads(''.join(lines))
        params['imgfname'] = img_fname
        params['outfilename'] = DATA_DIR + '/' +\
            pfbody + '_' + imfname.split('.')[0]
        shutil.move(pfname, pfname + '.bak')
    else:
        params = {}

    if opts:
        for k in opts:
            params[k] = opts[k]

    with open(params["paramfname"], "w") as f:
        json.dump(params, f, sort_keys=False, indent=4)


def pytest_funcarg__kn(request):
    DATA_DIR = '/home/skkmania/mnt2/workspace/pysrc/knbnk/data/1123003'
    img_fname = DATA_DIR + '/007.jpeg'
    params_fname = DATA_DIR + '/hough_1_2_100.json'
    kn = KnKoma(fname=img_fname, datadir=DATA_DIR, params=params_fname)
    return kn


def pytest_funcarg__kn2(request):
    fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
    params_file_name = DATA_DIR + '/twletters_01.json'
    return KnKoma(fname, params=params_file_name)


def pytest_funcarg__knManyLines(request):
    DATA_DIR = '/home/skkmania/mnt2/workspace/pysrc/knbnk/data/1142178'
    img_fname = DATA_DIR + '/007.jpeg'
    params_fname = DATA_DIR + '/o_011_ss_320_hgh_1_2_80_can_50_150_3_60.json'
    kn = KnKoma(fname=img_fname, datadir=DATA_DIR, params=params_fname)
    return kn


def pytest_funcarg__knFewLines(request):
    DATA_DIR = '/home/skkmania/mnt2/workspace/pysrc/knbnk/data/1123003'
    img_fname = DATA_DIR + '/006.jpeg'
    params_fname = DATA_DIR + '/hough_1_180_200.json'
    kn = KnKoma(fname=img_fname, datadir=DATA_DIR, params=params_fname)
    return kn


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


class TestSelectLine:
    def test_selectLine(self, knManyLines):
        knManyLines.prepareForLines()
        knManyLines.getHoughLines()
        result = knManyLines.enoughLines()
        assert result is True


class TestDivide:
    def test_divide(self, knManyLines):
        knManyLines.divide()
        assert knManyLines.leftPage is not None
        assert knManyLines.rightPage is not None


class TestEnoughLines:
    def test_makeCandidates(self, knManyLines):
        knManyLines.prepareForLines()
        knManyLines.getHoughLines()
        result = knManyLines.enoughLines()
        assert result is True

    def test_enoughLines(self, knManyLines):
        knManyLines.prepareForLines()
        knManyLines.getHoughLines()
        result = knManyLines.enoughLines()
        assert result is True

    def test_enoughLines2(self, knFewLines):
        knFewLines.prepareForLines()
        knFewLines.getHoughLines()
        result = knFewLines.enoughLines()
        assert result is False

    def test_partitionLines(self, kn):
        kn.prepareForLines()
        kn.getHoughLines()
        kn.partitionLines()
        assert kn.horizLines is not None
        assert kn.vertLines is not None


class TestFindCornerLines:
    def test_findCornerLines(self, knManyLines):
        knManyLines.prepareForLines()
        knManyLines.getHoughLines()
        knManyLines.enoughLines()
        knManyLines.findCornerLines()
        assert len(knManyLines.cornerLines) == 4
        knManyLines.findCenterLine()
        print str(knManyLines.cornerLines)
        assert len(knManyLines.cornerLines) == 5


class TestWriteSmallImage:
    def test_write_small_img(self):
        DATA_DIR = HOME_DIR + '/mnt2/workspace/pysrc/knbnk/data/1123003'
        opts = {
            "scale_size": 640.0,
            "boundingRect": [16, 32],
            "imgfname": DATA_DIR + "/007.jpeg",
            "outfilename": DATA_DIR + "/hough_1_180_200_007",
            "mode": "EXTERNAL",
            "canny": [50, 200, 3],
            "hough": [1, 180, 200],
            "paramfname": DATA_DIR + "/hough_1_180_200.json",
            "method": "NONE",
            "outdir": DATA_DIR
        }
        edit_parms_file(opts=opts)
        kn = KnKoma(params=opts["paramfname"])
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
        DATA_DIR = HOME_DIR + '/mnt2/workspace/pysrc/knbnk/data'
        img_fname = DATA_DIR + '/007.jpeg'
        params_fname = DATA_DIR + '/005_split_01.json'
        kn = KnKoma(fname=img_fname, datadir=DATA_DIR, params=params_fname)
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
        DATA_DIR = HOME_DIR + '/mnt2/workspace/pysrc/knbnk/data/1123003'
        edit_parms_file(pfbody, imfname, data_dir=DATA_DIR)
        params_fname = DATA_DIR + '/%s.json' % pfbody
        kn = KnKoma(params=params_fname)
        kn.prepareForLines()
        kn.getHoughLines()
        kn.get_small_img_with_lines()
        kn.write_small_img_with_lines(DATA_DIR)
        assert kn.small_img_with_lines is not None


class TestGetHoughLinesWithParamGenerator:
    def test_get_houghlines_with_param_generator(self):
        src = {
            "scale_size": [480.0, 320.0],
            "boundingRect": [[16, 32]],
            "imgfname": map(lambda x:
                            DATA_DIR + '/' + ('%03d' % x) + '.jpeg',
                            range(11, 21)),
            "mode": ["EXTERNAL"],
            "canny": [[50, 150, 3], [50, 100, 3]],
            "hough": [[1, 2, 80], [1, 90, 80], [1, 180, 150]],
            "method": ["NONE"],
            "outdir": [DATA_DIR]
        }
        result = params_generator(src)
        files = print_params_files(result)
        for params_fname in files:
            kn = KnKoma(params=params_fname)
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
