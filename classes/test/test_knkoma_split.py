# -*- coding: utf-8 -*-
import pytest
#import dircache
#import json
import os.path
#import shutil
import classes.knparam as kp
import classes.knkoma as kk
import classes.knutil as ku
import conftest as ct
# DATA_DIRにtar ballを置いておけばテストが走るという使い方をすること
#  例えば、1123033.tar.bz2をおいておきテストを実行すると
#  DATA_DIR/1123033 がつくられ、そこにparameter fileと結果のfileが展開される
#  そのためのparameterのデータはこのテスト用のファイルか、ここから読み込む
#  設定ファイルにおく
#  testを終え、必要な確認やデータの保存をすませたあとは
#  DATA_DIR/1123033は削除してしまえばよいものとする

HOME_DIR = 'Z:/Users/skkmania'
DATA_DIR = HOME_DIR + '/knbnk/data'


class TestEnoughLines:
    """
    線分が多い画像のとき、enoughLinesがTrueを返すことを確認
    (もっとも、これでもsmall_zone_levelsをいじったうえで実現しているのだが）
    画像も出力しているので目視確認せよ。
    """
    def test_enoughLines(self, knManyLines):
        knManyLines.set_logger("_enoughLines_M")
        k007 = kk.KnKoma(knManyLines)
        cf = ku.ImageManager(k007)
        cf.get_binarized("small")
        cf.getHoughLines()
        cf.get_small_img_with_lines()
        k007.write_small_img_with_lines()
        result = cf.enoughLines()
        assert result is True


class TestEnoughLinesFailure:
    """
    線分が少ない画像のとき、enoughLinesがFalseを返すことを確認
    画像も出力しているので目視確認せよ。
    """
    def test_enoughLines_Failure(self, knp):
        knp.set_logger("_hlfail")
        k001 = kk.KnKoma(knp)
        cf = ku.ImageManager(k001)
        cf.get_binarized("small")
        cf.getHoughLines()
        cf.get_small_img_with_lines()
        cf.write_small_img_with_lines()
        assert cf.enoughLines() is False


class TestDivide:
    def test_divide(self, knManyLines):
        knManyLines.set_logger("_divide_M")
        k007 = kk.KnKoma(knManyLines)
        k007.divide()
        assert k007.leftPage is not None
        assert k007.rightPage is not None


class TestMakePagesEnvironments:
    def test_make_pages_environment(self, knManyLines):
        knManyLines.set_logger("_mk_penv")
        k007 = kk.KnKoma(knManyLines)
        k007.make_pages_environment()
        assert os.path.exists(k007.right_page_fname)
        assert os.path.exists(k007.left_page_fname)


class TestMakePagesEnvironments2:
    def test_make_pages_environment2(self, knManyLines):
        knManyLines.set_logger("_mk_penv2")
        k007 = kk.KnKoma(knManyLines)
        k007.make_pages_environment()
        k007.write_binarized_file()
        k007.write_data_file()
        k007.write_small_img()
        k007.write_small_img_with_lines()
        k007.write_small_img_with_linesP()
        assert os.path.exists(k007.right_page_fname)
        assert os.path.exists(k007.left_page_fname)


class TestMakePagesEnvironments21:
    """
    parameter
    を変化させ、一度に実行し、その結果を比較する例
    これは、scale_sizeを３通り試している。
    この結果だけみると、320でじゅうぶん。
    もっとも、小さくしても処理時間の節約にはならなかったのであまり意味のないテストだった
    """
    def test_make_pages_environment21(self, knManyLines):
        vlist = {"koma": {"scale_size": [960.0, 640.0, 320.0]}}
        plist = ct.generate_param_dicts(knManyLines, vlist)
        for idx, p in enumerate(plist):
            with ku.Timer() as t:
                newParam = kp.KnParam(p)
                newParam.set_logger("_mk_penv21_%d" % idx)
                k007 = kk.KnKoma(newParam)
                k007.make_pages_environment()
                k007.write_binarized_file()
                k007.write_data_file()
                k007.write_small_img()
                k007.write_small_img_with_lines()
                k007.write_small_img_with_linesP()

            k007.logger.info("=> elasped time: %s s" % t.secs)
            assert os.path.exists(k007.right_page_fname)
            assert os.path.exists(k007.left_page_fname)


class TestMakePagesEnvironments3:
    def test_make_pages_environment3(self, knFewLines):
        knFewLines.set_logger("_mk_penv3")
        k007 = kk.KnKoma(knFewLines)
        k007.make_pages_environment()
        k007.write_binarized_file()
        k007.write_data_file()
        k007.write_small_img()
        k007.write_small_img_with_lines()
        k007.write_small_img_with_linesP()
        assert os.path.exists(k007.right_page_fname)
        assert os.path.exists(k007.left_page_fname)


class TestFindCornerLines:
    def test_findCornerLines(self, knManyLines):
        knManyLines.set_logger("_findCornerLines_M")
        k007 = kk.KnKoma(knManyLines)
        cf = ku.ImageManager(k007)
        cf.get_binarized("small")
        cf.getHoughLines()
        cf.enoughLines()
        cf.get_corner_lines()
        assert len(cf.cornerLines) == 5
        if cf.isCenterAmbiguous():
            cf.findCenterLine()
            k007.logger.debug(str(cf.cornerLines))
            assert len(cf.cornerLines) == 5


class TestWriteSmallImage:
    def test_write_small_img_with_lines_F(self, knFewLines):
        knFewLines.set_logger("_wswlF")
        k006 = kk.KnKoma(knFewLines)
        cf = ku.ImageManager(k006)
        cf.get_binarized("small")
        cf.getHoughLines()
        cf.get_small_img_with_lines()
        cf.write_small_img()
        cf.write_small_img_with_lines()
        assert cf.small_img is not None

    def test_write_small_img_with_lines_M(self, knManyLines):
        knManyLines.set_logger("_wswlM")
        k006 = kk.KnKoma(knManyLines)
        cf = ku.ImageManager(k006)
        cf.get_binarized("small")
        cf.getHoughLines()
        cf.write_small_img()
        cf.get_small_img_with_lines()
        cf.write_small_img_with_lines()
        assert cf.small_img is not None


class TestSmallImageP:
    def test_get_small_img_with_linesP(self, knManyLines):
        knManyLines.set_logger("_gslP")
        k006 = kk.KnKoma(knManyLines)
        im = ku.ImageManager(k006)
        im.get_binarized("small")
        im.getHoughLinesP()
        im.get_small_img_with_linesP()
        k006.write_small_img_with_linesP()
        im.write_linesP_to_file()
        im.write_lines_to_file()
        assert im.small_img_with_linesP is not None


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
            "koma": {
                "scale_size": [480.0, 320.0],
                "canny": [[50, 150, 3], [50, 100, 3]],
                "hough": [[1, 2, 80], [1, 90, 80], [1, 180, 150]]
            },
            "page": {
                "boundingRect": [[16, 32]],
                "mode": ["EXTERNAL"],
                "method": ["NONE"],
                "canny": [[50, 150, 3], [50, 100, 3]]
            },
            "komanumstr": ["001"],
            "imgfname": map(lambda x:
                            data_dir + '/' + ('%03d' % x) + '.jpeg',
                            range(11, 21)),
        }
        result = ku.params_generator(src)
        files = ku.print_params_files(result)
        for params_fname in files:
            kn = kk.KnKoma(params=params_fname)
            im = ku.ImageManager(kn)
            im.get_binarized("small")
            im.getHoughLines()
            im.get_small_img_with_lines()
            kn.write_small_img_with_lines()
            assert im.small_img_with_lines is not None
