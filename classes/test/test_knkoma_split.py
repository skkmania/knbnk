# -*- coding: utf-8 -*-
import pytest
#import dircache
import json
import shutil
import classes.knkoma as kk
import classes.knutil as ku
# DATA_DIRにtar ballを置いておけばテストが走るという使い方をすること
#  例えば、1123033.tar.bz2をおいておきテストを実行すると
#  DATA_DIR/1123033 がつくられ、そこにparameter fileと結果のfileが展開される
#  そのためのparameterのデータはこのテスト用のファイルか、ここから読み込む
#  設定ファイルにおく
#  testを終え、必要な確認やデータの保存をすませたあとは
#  DATA_DIR/1123033は削除してしまえばよいものとする

HOME_DIR = u"/home/skkmania"
DATA_DIR = HOME_DIR + u"/mnt2/workspace/pysrc/knbnk/data"


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
        params['komanumstr'] = imfname.split('.')[0]
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


class TestGetHoughLinesP:
    def test_getHoughLinesP(self):
        bookId = '1123003'
        data_dir = DATA_DIR + '/' + bookId
        params = {
            "komanumstr": "007",
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
        ku.check_test_environment(params, bookId)
        kns = kk.KnKoma(params=params['paramfname'])
        kns.prepareForLines()
        kns.getHoughLinesP()
        kns.write_linesP_to_file(data_dir)


class TestGetHoughLines:
    def pytest_funcarg__kns(self, request):
        bookId = '1123003'
        self.data_dir = DATA_DIR + '/' + bookId
        params = {
            "scale_size": 640.0,
            "komanumstr": "007",
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
        ku.check_test_environment(params, bookId)
        return kk.KnKoma(params=params['paramfname'])

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


class TestEnoughLinesFailure:
    def pytest_funcarg__kns(self, request):
        bookId = '1091460'
        self.data_dir = DATA_DIR + '/' + bookId
        params = {
            "scale_size": 640.0,
            "komanumstr": "007",
            "boundingRect": [16, 32],
            "imgfname": self.data_dir + '/001.jpeg',
            "outfilename": "hough_1_2_100_001",
            "mode": "EXTERNAL",
            "canny": [50, 150, 3],
            "hough": [1, 2, 50],
            "paramfname": self.data_dir + '/hough_1_2_100.json',
            "method": "NONE",
            "outdir": self.data_dir
        }
        ku.check_test_environment(params, bookId)
        return kk.KnKoma(params=params['paramfname'])

    def test_prepareForLines(self, kns):
        kns.prepareForLines()

    def test_getHoughLines(self, kns):
        kns.prepareForLines()
        kns.getHoughLines()
        assert kns.enoughLines() is False


class TestDivide:
    def test_divide(self, knManyLines):
        knManyLines.set_logger("_divide_M")
        k007 = kk.KnKoma(knManyLines)
        k007.divide()
        assert k007.leftPage is not None
        assert k007.rightPage is not None


class TestDivideFailure:
    def test_divide(self, knFewLines):
        knFewLines.set_logger("_divide_F")
        k007 = kk.KnKoma(knFewLines)
        k007.divide()
        assert k007.leftPage is not None
        assert k007.rightPage is not None


class TestEnoughLines:
    def test_enoughLines(self, knManyLines):
        knManyLines.set_logger("_enoughLines_M")
        k007 = kk.KnKoma(knManyLines)
        k007.prepareForLines()
        k007.getHoughLines()
        result = k007.enoughLines()
        assert result is False

    def test_enoughLines2(self, knFewLines):
        knFewLines.set_logger("_enoughLines_F")
        k007 = kk.KnKoma(knFewLines)
        k007.prepareForLines()
        k007.getHoughLines()
        result = k007.enoughLines()
        assert result is False


class TestFindCornerLines:
    def test_findCornerLines(self, knManyLines):
        knManyLines.set_logger("_findCornerLines_M")
        k007 = kk.KnKoma(knManyLines)
        cf = ku.CornerLineFinder(k007)
        cf.prepareForLines()
        cf.getHoughLines()
        cf.enoughLines()
        cf.get_corner_lines()
        assert len(cf.cornerLines) == 5
        if cf.isCenterAmbiguous():
            cf.findCenterk007Line()
            print str(cf.cornerLines)
            assert len(cf.cornerLines) == 5


class TestWriteSmallImage:
    def test_write_small_img(self, knFewLines):
        knFewLines.set_logger("_wsmi")
        k006 = kk.KnKoma(knFewLines)
        k006.prepareForLines()
        k006.write_small_img()
        assert k006.small_img is not None

    def test_write_small_img_with_lines_F(self, knFewLines):
        knFewLines.set_logger("_wswlF")
        k006 = kk.KnKoma(knFewLines)
        k006.prepareForLines()
        k006.getHoughLines()
        k006.get_small_img_with_lines()
        k006.write_small_img_with_lines()
        assert k006.small_img is not None

    def test_write_small_img_with_lines_M(self, knManyLines):
        knManyLines.set_logger("_wswlM")
        k006 = kk.KnKoma(knManyLines)
        k006.prepareForLines()
        k006.getHoughLines()
        k006.get_small_img_with_lines()
        k006.write_small_img_with_lines()
        assert k006.small_img is not None


class TestSmallImageP:
    def test_get_small_img_with_linesP(self, knManyLines):
        knManyLines.set_logger("_gslP")
        k006 = kk.KnKoma(knManyLines)
        k006.prepareForLines()
        k006.getHoughLinesP()
        k006.get_small_img_with_linesP()
        k006.write_small_img_with_linesP()
        assert k006.small_img_with_linesP is not None


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
        pass


class TestGetHoughLinesWithParamGenerator:
    def test_get_houghlines_with_param_generator(self):
        bookId = '1142178'
        data_dir = DATA_DIR + '/' + bookId
        ku.check_book_directory(bookId)
        src = {
            "scale_size": [480.0, 320.0],
            "boundingRect": [[16, 32]],
            "komanumstr": ["001"],
            "imgfname": map(lambda x:
                            data_dir + '/' + ('%03d' % x) + '.jpeg',
                            range(11, 21)),
            "mode": ["EXTERNAL"],
            "canny": [[50, 150, 3], [50, 100, 3]],
            "hough": [[1, 2, 80], [1, 90, 80], [1, 180, 150]],
            "method": ["NONE"],
            "outdir": [data_dir]
        }
        result = ku.params_generator(src)
        files = ku.print_params_files(result)
        for params_fname in files:
            kn = kk.KnKoma(params=params_fname)
            kn.prepareForLines()
            kn.getHoughLines()
            kn.get_small_img_with_lines()
            kn.write_small_img_with_lines()
            assert kn.small_img_with_lines is not None
