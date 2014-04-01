# -*- coding: utf-8 -*-
from classes.knparam import *
import pytest

DATA_DIR = '/home/skkmania/mnt2/workspace/pysrc/knbnk/data'


class TestNew:
    def test_initialize_without_params(self):
        with pytest.raises(KnParamException) as e:
            KnParam()
        assert 'must specify' in str(e)

    def test_initialize_with_fname_not_existed(self):
        with pytest.raises(KnParamParamsException) as e:
        #with pytest.raises(KnParamException) as e:
            KnParam(param_fname='not_exist_file')
        assert 'not_exist_file' in str(e)

    def test_initialize_with_imcomplete_param_file(self):
        with pytest.raises(KnParamParamsException) as e:
            KnParam(param_fname=DATA_DIR + '/imcomplete_sample.json')
        assert 'must be' in str(e)

    def test_new(self, knp):
        assert knp.datadir() == DATA_DIR