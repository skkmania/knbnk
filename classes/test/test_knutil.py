# -*- coding: utf-8 -*-
import classes.knutil as ku

HOME_DIR = '/home/skkmania'
DATA_DIR = HOME_DIR + '/mnt2/workspace/pysrc/knbnk/data/twletters'
img_fname = DATA_DIR + '/twletters.jpg'


class TestCheckTestEnvironment:
    def test_check_test_environment1(self, b1g101):
        assert b1g101 is not None

    def test_check_test_environment2(self, b1g102):
        assert b1g102 is not None


class TestFileName:
    def test_mkFilename(self, kn):
        name = ku.mkFilename(kn, '_cont')
        expect = DATA_DIR + '/twl_can_50_200_hough_1_2_100_cont.jpg'
        assert name == expect

    def test_write_data_file(self, kn):
        kn.write_data_file(DATA_DIR)


class TestTmpDir:
    def test_write(self, tmpdir):
        dataDirectory = tmpdir.mkdir('data')
        sampleFile = str(dataDirectory.join("sample.jpeg"))
        ku.write(sampleFile)
        assert 'sample.jpeg' in sampleFile
        assert sampleFile != '/tmp/pytest-skkmania/data/sample.jpeg'


class TestParamsGenerator:
    def test_params_generator(self, tmpdir):
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
        src = SRC_SAMPLE
        result = ku.params_generator(src)
        wrap = lambda d: d.get("scale_size")
        assert set(map(wrap, result)) == set(src["scale_size"])
        dataDirectory = tmpdir.mkdir('data')
        sampleFile = dataDirectory.join("result.txt")
        with open(str(sampleFile), 'w') as f:
            f.write(str(result))
        ku.print_params_files(result)
