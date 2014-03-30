# -*- coding: utf-8 -*-
import pytest
from classes.knkoma import *
from classes.knpage import *
from classes.knutil import *
from classes.knbook import *

DATA_DIR = '/home/skkmania/mnt2/workspace/pysrc/knbnk/data'


class TestBook:
    def test_new(self, knbk1):
        assert knbk1 is not None

    def test_(self, knbk1):
        pass
