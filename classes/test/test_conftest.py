# -*- coding: utf-8 -*-
#import pytest
#import dircache
#import os.path
#import classes.knkoma as kk
#import classes.knutil as ku
import conftest as cf

HOME_DIR = 'Z:/Users/skkmania'
DATA_DIR = HOME_DIR + '/knbnk/data'


class TestGenerateParamDicts:
    def test_generate_param_dicts(self, tmpdir):
        result = cf.generate_param_dicts(param_dict={"a": {"b": 10}},
                                         v_list={"a": {"b": [15, 20, 30, 40]}})
        assert {"a": {"b": 15}} in result
        assert {"a": {"b": 20}} in result
        assert {"a": {"b": 30}} in result
        assert {"a": {"b": 40}} in result
        dataDirectory = tmpdir.mkdir('data')
        sampleFile = dataDirectory.join("result.txt")
        with open(str(sampleFile), 'w') as f:
            f.write(str(result))
