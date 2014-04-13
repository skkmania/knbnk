# -*- coding: utf-8 -*-
import logging
#import pytest
import os.path
#import classes.knkoma as kk
#import classes.knpage as kp
#import classes.knutil as ku
#import classes.knbook as kb

DATA_DIR = '/home/skkmania/mnt2/workspace/pysrc/knbnk/data'


class TestBook:
    def test_new(self, knbk1):
        assert knbk1 is not None

    def test_start(self, knbk1):
        pass

    def test_read_metadata(self, knbk1):
        knbk1.read_metadata()
        assert knbk1.metadata is not None
        assert knbk1.metadata['id'] == knbk1.p.bookId()
        assert knbk1.komanum == 10

    def test_mkKomaParam(self, knbk1):
        knbk1.read_metadata()
        knbk1.p.mkKomaParam(1)
        assert os.path.exists(knbk1.p.outdir() + '/k_001.json')

    def test_divide_all(self, knbk1):
        logging.basicConfig(filename=
                            knbk1.p.workdir() + '/test_divide_all.log',
                            level=logging.DEBUG,
                            format='%(asctime)s %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p')
        knbk1.logger.debug(str(knbk1.p))
        knbk1.read_metadata()
        knbk1.divide_all()
