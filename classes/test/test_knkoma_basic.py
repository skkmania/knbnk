# -*- coding: utf-8 -*-
import pytest
import hamcrest as h
import classes.knkoma as kk
import classes.knutil as ku
import classes.knparam as kp

HOME_DIR = '/home/skkmania'
DATA_DIR = HOME_DIR + '/mnt2/workspace/pysrc/knbnk/data'


def pytest_funcarg__param_obj(request):
    bookId = 'twletters'
    params = {
        "param": {
            "arcdir":      DATA_DIR,
            "paramfdir":   bookId,
            "workdir":     DATA_DIR,
            "outdir":      "/".join([DATA_DIR, bookId]),
            "paramfname":  "knkoma1.json",
            "logfilename": "knkoma1",
            "balls":       [bookId]
        },
        "book": {
            "bookdir":      bookId,
            "bookId":       bookId
        },
        "koma": {
            "komadir":      "k001",
            "komaId":       1,
            "komaIdStr":    "001",
            "scale_size":   640.0,
            "hough":        [1, 2, 100],
            "canny":        [50, 200, 3],
            "imgfname":     "001.jpeg"
        },
        "page": {
            "pagedir":      "/".join(['can_50_200_3', 'hgh_1_2_100', 'right']),
            "imgfname":     "001_0.jpeg",
            "lr":           "right",
            "boundingRect": [16, 32],
            "mode":         "EXTERNAL",
            "method":       "NONE",
            "mavstd":       10,
            "pgmgn":        [0.05, 0.05],
            "ismgn":        [15, 5],
            "toobig":       [200, 200],
            "canny":        [50, 200, 3]
        }
    }
    return kp.KnParam(params)


class TestNew:
    def test_initialize_without_params(self):
        with pytest.raises(kk.KnKomaException) as e:
            kk.KnKoma()
        assert 'param must be specified' in str(e)

    def test_initialize_with_fname_not_existed(self):
        with pytest.raises(kk.KnKomaParamsException) as e:
            kk.KnKoma(param='not_exist_file')
        assert 'param must be KnParam' in str(e)

    def test_new(self, param_obj):
        param_obj.set_logger("_knkoma1")
        knkoma1 = kk.KnKoma(param_obj)
        assert knkoma1.img is not None
        assert knkoma1.img.shape != (100, 100, 3)
        assert knkoma1.img.shape == (3226, 4878, 3)
        assert knkoma1.height == 3226
        assert knkoma1.width == 4878
        assert knkoma1.depth == 3
        assert knkoma1.gray is not None
        assert knkoma1.binarized is not None

    def test_new_try_hamcrest(self, param_obj):
        param_obj.set_logger("_hamcrest")
        knkoma1 = kk.KnKoma(param_obj)
        h.assert_that(knkoma1.height, h.equal_to(3226))


class TestWriteFiles:
    def test_write_files(self, param_obj):
        param_obj.set_logger("_write_files")
        kn2 = kk.KnKoma(param_obj)
        kn2.write_data_file()
        kn2.write_binarized_file()


class TestFileName:
    def test_mkFilename(self, knp):
        data_dir = DATA_DIR
        knp.set_logger("_mkFilename")
        kn = kk.KnKoma(knp)
        name = ku.mkFilename(kn, '_cont')
        expect = data_dir + '/1091460/k001/001_cont.jpeg'
        assert name == expect

    def test_write_data_file(self, knp):
        knp.set_logger("_write_data_file")
        kn = kk.KnKoma(knp)
        kn.write_data_file(DATA_DIR)


class TestEstimateLayouts:
    def test_estimate_layouts_of_graph2(self, graph2):
        graph2.set_logger("_estimate_layouts_of_graph2")
        kn = kk.KnKoma(graph2)
        kn.write_binarized_file()
        kn.estimate_layouts()
        assert type(kn.layouts) is list
        assert len(kn.layouts) == 2

    def test_estimate_layouts_of_b1g101(self, b1g101):
        b1g101.set_logger("_estimate_layouts_of_b1g101")
        kn = kk.KnKoma(b1g101)
        kn.write_binarized_file()
        kn.estimate_layouts()
        assert type(kn.layouts) is list
        assert len(kn.layouts) == 2

    def test_estimate_layouts_of_b1g102(self, b1g102):
        b1g102.set_logger("_estimate_layouts_of_b1g102")
        kn = kk.KnKoma(b1g102)
        kn.write_binarized_file()
        kn.estimate_layouts()
        assert type(kn.layouts) is list
        assert len(kn.layouts) == 2
