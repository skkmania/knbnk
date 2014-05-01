# -*- coding: utf-8 -*-
#import logging
#import pytest
#import classes.knkoma as kk
#import classes.knpage as kp
#import classes.knutil as ku
import classes.knbook as kb

DATA_DIR = '/home/skkmania/mnt2/workspace/pysrc/knbnk/data'


class TestBook:
    def test_new(self, knbk1):
        knbk1.set_logger("_new")
        b = kb.KnBook(knbk1)
        assert b is not None

    def test_read_metadata(self, knbk1):
        knbk1.set_logger("_read_metadata")
        b = kb.KnBook(knbk1)
        assert b.metadata is not None
        assert b.metadata['id'] == knbk1['book']['bookId']
        assert b.komanum == 10

    def test_check_komanum(self, knbk1):
        knbk1.set_logger("_check_komanum")
        b = kb.KnBook(knbk1)
        b.check_komanum()


class TestGenerateKoma:
    def test_generate_a_koma(self, knbk1):
        knbk1.set_logger("_generate_a_koma")
        b = kb.KnBook(knbk1)
        k = b.generate_a_koma(2)
        assert k is not None


class TestDivideAll:
    def test_divide_all(self, knbk1):
        knbk1.set_logger("_divide_all")
        b = kb.KnBook(knbk1)
        b.divide_all()


class TestStart:
    def test_start(self, knbk1):
        knbk1.set_logger("_start")
        b = kb.KnBook(knbk1)
        b.start()
