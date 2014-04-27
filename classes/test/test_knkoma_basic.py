# -*- coding: utf-8 -*-
import pytest
import hamcrest as h
import classes.knkoma as kk
import classes.knutil as ku
import classes.knparam as kp

HOME_DIR = '/home/skkmania'
DATA_DIR = HOME_DIR + '/mnt2/workspace/pysrc/knbnk/data'


def pytest_funcarg__knkoma1(request):
    bookId = 'twletters'
    params = {
        "param": {
            "arcdir":      DATA_DIR,
            "paramfdir":   "/".join([DATA_DIR, bookId]),
            "workdir":     "/".join([DATA_DIR, bookId]),
            "outdir":      "/".join([DATA_DIR, bookId]),
            "paramfname":  "/".join([DATA_DIR, bookId, "knkoma1.json"]),
            "logfilename": "/".join([DATA_DIR, bookId, "knkoma1.log"]),
            "balls":       []
        },
        "book": {
            "bookdir":      "/".join([DATA_DIR, bookId]),
            "bookId":       bookId
        },
        "koma": {
            "komadir":       "/".join([DATA_DIR, bookId]),
            "komaId":       1,
            "komaIdStr":    "001",
            "scale_size":   640.0,
            "hough":        [1, 2, 100],
            "canny":        [50, 200, 3],
            "imgfname":     "001.jpeg"
        },
        "page": {
            "pagedir":      "/".join([DATA_DIR, bookId, 'k001',
                                      'can_50_200',
                                      'hgh_1_2_100', 'right']),
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
        },
        "layout": {
        },
        "char": {
        },
        "spec": {}
    }
    param_obj = kp.KnParam(params)
    return kk.KnKoma(param_obj)


class TestNew:
    def test_initialize_without_params(self):
        with pytest.raises(kk.KnKomaException) as e:
            kk.KnKoma()
        assert 'param must be specified' in str(e)

    def test_initialize_with_fname_not_existed(self):
        with pytest.raises(kk.KnKomaParamsException) as e:
            kk.KnKoma(param='not_exist_file')
        assert 'param must be KnParam' in str(e)

    def test_new(self, knkoma1):
        assert knkoma1.img is not None
        assert knkoma1.img.shape != (100, 100, 3)
        assert knkoma1.img.shape == (3226, 4878, 3)
        assert knkoma1.height == 3226
        assert knkoma1.width == 4878
        assert knkoma1.depth == 3
        assert knkoma1.gray is not None
        assert knkoma1.binarized is not None

    def test_new_try_hamcrest(self, knkoma1):
        h.assert_that(knkoma1.height, h.equal_to(3226))


class TestParams:
    def pytest_funcarg__kn(request):
        paramfname = DATA_DIR + '/twletters/twletters_01.json'
        return kk.KnKoma(kp.KnParam(param_fname=paramfname))

    def pytest_funcarg__kn2(request):
        fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
        params_file_name = DATA_DIR + '/twletters/twletters_01.json'
        return kk.KnKoma(fname, params=params_file_name)

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
    def pytest_funcarg__kn(request):
        paramfname = DATA_DIR + '/twletters/twletters_01.json'
        return kk.KnKoma(kp.KnParam(param_fname=paramfname))

    def test_write(self, kn, tmpdir):
        dataDirectory = tmpdir.mkdir('data')
        sampleFile = str(dataDirectory.join("sample.jpeg"))
        kn.write(sampleFile)
        assert 'sample.jpeg' in sampleFile


class TestFileName:
    def test_mkFilename(self, knp):
        data_dir = DATA_DIR
        kn = kk.KnKoma(knp)
        name = ku.mkFilename(kn, '_cont')
        expect = data_dir + '/1091460/k001/001_cont.jpeg'
        assert name == expect

    def test_write_data_file(self, knp):
        kn = kk.KnKoma(knp)
        kn.write_data_file(DATA_DIR)


class TestEstimateLayouts:
    def test_estimate_layouts_of_graph2(self, graph2):
        kn = kk.KnKoma(graph2)
        kn.write_binarized_file()
        kn.estimate_layouts()
        assert type(kn.layouts) is list
        assert len(kn.layouts) == 2

    def test_estimate_layouts_of_b1g101(self, b1g101):
        kn = kk.KnKoma(b1g101)
        kn.write_binarized_file()
        kn.estimate_layouts()
        assert type(kn.layouts) is list
        assert len(kn.layouts) == 2

    def test_estimate_layouts_of_b1g102(self, b1g102):
        kn = kk.KnKoma(b1g102)
        kn.write_binarized_file()
        kn.estimate_layouts()
        assert type(kn.layouts) is list
        assert len(kn.layouts) == 2
