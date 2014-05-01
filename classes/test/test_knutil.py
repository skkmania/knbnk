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
