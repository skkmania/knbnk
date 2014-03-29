# -*- coding: utf-8 -*-
import pytest
import os
import os.path
#import dircache
import json
import shutil
import itertools

from classes.knkoma import KnKoma
from classes.knutil import *

# DATA_DIRにtar ballを置いておけばテストが走るという使い方をすること
#  例えば、1123033.tar.bz2をおいておきテストを実行すると
#  DATA_DIR/1123033 がつくられ、そこにparameter fileと結果のfileが展開される
#  そのためのparameterのデータはこのテスト用のファイルか、ここから読み込む
#  設定ファイルにおく
#  testを終え、必要な確認やデータの保存をすませたあとは
#  DATA_DIR/1123033は削除してしまえばよいものとする

HOME_DIR = u"/home/skkmania"
DATA_DIR = HOME_DIR + u"/mnt2/workspace/pysrc/knbnk/data"
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


def check_test_environment(params, bookId):
    """
    paramsに記述されたoutdirの存在確認
      なければ、tarballの展開とoutdirの作成
    parmsのtxt file( json format)の作成は常に行う
    (testのたびにそのtestの設定を使うこと。
    別のtestの影響を受けたくないので。)
    """
    if not os.path.exists(params['outdir']):
        cmd = 'tar jxf %s/%s.tar.bz2 -C %s' % (DATA_DIR, bookId, DATA_DIR)
        os.system(cmd)
        cmd = "find %s -type d -name '*%s*' -exec mv {} %s \\;" %\
            (DATA_DIR, bookId, params["outdir"])
        os.system(cmd)

    print_params_files([params])


def check_book_directory(bookId):
    """
    outdir = DATA_DIR + '/' + bookId の存在確認
      なければ、tarballの展開とoutdirの作成
    """
    outdir = DATA_DIR + '/' + bookId
    if not os.path.exists(outdir):
        cmd = 'tar jxf %s/%s.tar.bz2 -C %s' % (DATA_DIR, bookId, DATA_DIR)
        os.system(cmd)
        cmd = "find %s -type d -name '*%s*' -exec mv {} %s \\;" %\
            (DATA_DIR, bookId, outdir)
        os.system(cmd)


class TestCheckTestEnvironment:
    @pytest.mark.parametrize("bookId", [
        "1092905", "1091460"
    ])
    def test_check_test_environment(self, bookId):
        params = {'outdir': DATA_DIR + "/" + bookId,
                  'paramfname': DATA_DIR + "/" + bookId + "/test_made.json",
                  }
        if os.path.exists(params['outdir']):
            cmd = 'rm -rf ' + params['outdir']
            os.system(cmd)
        check_test_environment(params, bookId)
        result = os.path.exists(params['outdir'])
        assert result is True


def mk_params_file(params):
    """
    入力: dict型 : parametersが列挙されている。
    戻り値: なし。
    副作用: 単体のparameter fileが作成される。(json形式のtext file)
            作成されるfileの場所、名前はparams自身に記されているとおり
    """
    fname = params['paramfname']
    with open(fname, 'w') as f:
        json.dump(params, f, sort_keys=False, indent=4)


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
    params = {
        "scale_size": 640.0,
        "boundingRect": [16, 32],
        "hough": [1, 2, 100],
        "imgfname": "/home/skkmania/mnt2/workspace/pysrc/knbnk/data/1123003/007.jpeg",
        "outfilename": "hough_1_2_100_007",
        "mode": "EXTERNAL",
        "canny": [50, 200, 3],
        "paramfname": "/home/skkmania/mnt2/workspace/pysrc/knbnk/data/1123003/hough_1_2_100.json",
        "method": "NONE",
        "outdir": "/home/skkmania/mnt2/workspace/pysrc/knbnk/data/1123003"
    }
    check_test_environment(params, '1123003')
    return KnKoma(params=params['paramfname'])


def pytest_funcarg__knManyLines(request):
    params = {
        "scale_size": 320.0,
        "boundingRect": [16, 32],
        "hough": [1, 2, 80],
        "imgfname": "/home/skkmania/mnt2/workspace/pysrc/knbnk/data/1142178/007.jpeg",
        "outfilename": "o_007_ss_320_hgh_1_2_80_can_50_150_3_60",
        "mode": "EXTERNAL",
        "canny": [50, 150, 3],
        "paramfname": "/home/skkmania/mnt2/workspace/pysrc/knbnk/data/1142178/o_007_ss_320_hgh_1_2_80_can_50_150_3_60.json",
        "method": "NONE",
        "outdir": "/home/skkmania/mnt2/workspace/pysrc/knbnk/data/1142178"
    }
    check_test_environment(params, '1142178')
    return KnKoma(params=params['paramfname'])


def pytest_funcarg__knFewLines(request):
    params = {
        "scale_size": 320.0,
        "boundingRect": [16, 32],
        "hough": [1, 180, 200],
        "imgfname": "/home/skkmania/mnt2/workspace/pysrc/knbnk/data/1123003/006.jpeg",
        "outfilename": "o_006_ss_320_hgh_1_180_200_can_50_150_3_60",
        "mode": "EXTERNAL",
        "canny": [50, 150, 3],
        "paramfname": "/home/skkmania/mnt2/workspace/pysrc/knbnk/data/1123003/o_006_ss_320_hgh_1_180_200_can_50_150_3_60.json",
        "method": "NONE",
        "outdir": "/home/skkmania/mnt2/workspace/pysrc/knbnk/data/1123003"
    }
    check_test_environment(params, '1123003')
    return KnKoma(params=params['paramfname'])


class TestGetHoughLinesP:
    def test_getHoughLinesP(self):
        bookId = '1123003'
        data_dir = DATA_DIR + '/' + bookId
        params = {
            "scale_size": 640.0,
            "boundingRect": [16, 32],
            "imgfname": data_dir + '/007.jpeg',
            "outfilename": "hough_1_2_100_007",
            "mode": "EXTERNAL",
            "canny": [50, 200, 3],
            "hough": [1, 2, 100],
            "paramfname": data_dir + '/hough_1_2_100.json',
            "method": "NONE",
            "outdir": data_dir
        }
        check_test_environment(params, bookId)
        kns = KnKoma(params=params['paramfname'])
        kns.prepareForLines()
        kns.getHoughLinesP()
        kns.write_linesP_to_file(data_dir)


class TestGetHoughLines:
    def pytest_funcarg__kns(self, request):
        bookId = '1123003'
        self.data_dir = DATA_DIR + '/' + bookId
        params = {
            "scale_size": 640.0,
            "boundingRect": [16, 32],
            "imgfname": self.data_dir + '/007.jpeg',
            "outfilename": "hough_1_2_100_007",
            "mode": "EXTERNAL",
            "canny": [50, 200, 3],
            "hough": [1, 2, 100],
            "paramfname": self.data_dir + '/hough_1_2_100.json',
            "method": "NONE",
            "outdir": self.data_dir
        }
        check_test_environment(params, bookId)
        return KnKoma(params=params['paramfname'])

    def test_prepareForLines(self, kns):
        kns.prepareForLines()

    def test_getHoughLines(self, kns):
        kns.prepareForLines()
        kns.getHoughLines()

    def test_write_lines_to_file(self, kns):
        kns.prepareForLines()
        kns.getHoughLines()
        kns.write_lines_to_file(self.data_dir)
        assert len(kns.lines) > 0


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
        params = {
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
        check_test_environment(params, '1123003')
        kn = KnKoma(params=params["paramfname"])
        kn.prepareForLines()
        kn.write_small_img(DATA_DIR)
        assert kn.small_img is not None


class TestSmallImage:
    def test_get_small_img_with_lines(self, kn):
        kn.prepareForLines()
        kn.getHoughLines()
        kn.get_small_img_with_lines()
        assert kn.small_img is not None

    def test_write_small_img(self, kn):
        kn.prepareForLines()
        kn.getHoughLines()
        kn.write_small_img()
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
        check_book_directory('1123003')
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
        bookId = '1142178'
        data_dir = DATA_DIR + '/' + bookId
        check_book_directory(bookId)
        src = {
            "scale_size": [480.0, 320.0],
            "boundingRect": [[16, 32]],
            "imgfname": map(lambda x:
                            data_dir + '/' + ('%03d' % x) + '.jpeg',
                            range(11, 21)),
            "mode": ["EXTERNAL"],
            "canny": [[50, 150, 3], [50, 100, 3]],
            "hough": [[1, 2, 80], [1, 90, 80], [1, 180, 150]],
            "method": ["NONE"],
            "outdir": [data_dir]
        }
        result = params_generator(src)
        files = print_params_files(result)
        for params_fname in files:
            kn = KnKoma(params=params_fname)
            kn.prepareForLines()
            kn.getHoughLines()
            kn.get_small_img_with_lines()
            kn.write_small_img_with_lines()
            assert kn.small_img_with_lines is not None


class TestSmallImageP:
    def test_get_small_img_with_linesP(self, kn):
        kn.prepareForLines()
        kn.getHoughLinesP()
        kn.get_small_img_with_linesP()
        kn.write_small_img_with_linesP()
        assert kn.small_img_with_linesP is not None
