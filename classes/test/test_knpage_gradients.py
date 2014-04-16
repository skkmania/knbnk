# -*- coding: utf-8 -*-
import pytest
import classes.knpage as kp
import classes.knutil as ku

DATA_DIR = '/home/skkmania/mnt2/workspace/pysrc/knbnk/data'


class TestWriteGradients:
    @pytest.mark.parametrize("sobel", [
        [6, 1, 0, 5],
        [6, 1, 1, 5],
        [6, 0, 1, 5]
    ])
    def test_write_gradients(self, sobel):
        bookId = 'twletters'
        params = {
            "scale_size":   640.0,
            "imgfname":     "/".join([DATA_DIR, bookId, "twletters.jpg"]),
            "outdir":       "/".join([DATA_DIR, bookId]),
            "paramfname":   "/".join([DATA_DIR, bookId, "twl_sobel.json"]),
            "outfilename":  "auto",
            "boundingRect": [16, 32],
            "mode":         "TREE",
            "method":       "NONE",
            "sobel":        sobel,
            "scharr":       [-1, 0, 1]
        }
        ku.print_params_files([params])
        ku.check_test_environment(params, bookId)
        knSobel = kp.KnPage(params=params['paramfname'])
        knSobel.getGradients()
        knSobel.write_gradients()


class TestWriteScharr:
    @pytest.mark.parametrize("scharr", [
        [-1, 0, 1],
        [-1, 1, 0]
    ])
    def test_write_gradients(self, scharr):
        bookId = 'twletters'
        params = {
            "scale_size":   640.0,
            "imgfname":     "/".join([DATA_DIR, bookId, "twletters.jpg"]),
            "outdir":       "/".join([DATA_DIR, bookId]),
            "paramfname":   "/".join([DATA_DIR, bookId, "twl_scharr.json"]),
            "outfilename":  "auto",
            "boundingRect": [16, 32],
            "mode":         "TREE",
            "method":       "NONE",
            "scharr":       scharr
        }
        ku.print_params_files([params])
        ku.check_test_environment(params, bookId)
        knSobel = kp.KnPage(params=params['paramfname'])
        knSobel.getGradients()
        knSobel.write_gradients()
