# -*- coding: utf-8 -*-
import logging
from classes.knparam import *
import pytest

DATA_DIR = '/home/skkmania/mnt2/workspace/pysrc/knbnk/data'


class TestNew:
    def test_initialize_without_params(self):
        with pytest.raises(KnParamParamsException) as e:
            KnParam()
        assert 'must be specified' in str(e)

    def test_initialize_with_fname_not_existed(self):
        with pytest.raises(KnParamParamsException) as e:
        #with pytest.raises(KnParamException) as e:
            KnParam(param_fname='not_exist_file')
        assert 'not_exist_file' in str(e)

    def test_initialize_with_syntax_error_param_file(self):
        with pytest.raises(ValueError) as e:
            KnParam(param_fname=DATA_DIR + '/params_with_syntax_error.json')
        assert 'Expecting' in str(e)

    def test_initialize_with_lack(self):
        with pytest.raises(KnParamParamsException) as e:
            KnParam(param_fname=DATA_DIR + '/params_lacks.json')
        assert 'lacks' in str(e)

    def test_new_from_file(self, knp):
        logging.basicConfig(level=logging.DEBUG)
        knp.logger.debug(str(knp))
        assert knp['workdir'] == DATA_DIR + '/1091460'

    def test_new_from_dict(self, knpd):
        logging.basicConfig(level=logging.DEBUG)
        knpd.logger.debug(str(knpd))
        assert knpd['workdir'] == DATA_DIR + '/1091460'
