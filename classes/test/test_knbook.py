# -*- coding: utf-8 -*-
import logging
import pytest
import os.path
from classes.knkoma import *
from classes.knpage import *
from classes.knutil import *
from classes.knbook import *

DATA_DIR = '/home/skkmania/mnt2/workspace/pysrc/knbnk/data'


class TestBook:
    def test_new(self, knbk1):
        assert knbk1 is not None

    def test_read_metadata(self, knbk1):
        knbk1.read_metadata()
        assert knbk1.metadata is not None
        assert knbk1.metadata['id'] == knbk1.param.bookId()
        assert knbk1.komanum == 10

    def test_mkKomaParam(self, knbk1):
        knbk1.read_metadata()
        knbk1.param.mkKomaParam(1)
        assert os.path.exists(knbk1.param.outdir() + '/k_001.json')

    def test_divide_all(self, knbk1):
        logging.basicConfig(filename=
                            knbk1.param.workdir() + '/test_divide_all.log',
                            level=logging.DEBUG)
        knbk1.read_metadata()
        knbk1.divide_all()
