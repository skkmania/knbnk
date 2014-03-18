# -*- coding: utf-8 -*-
import write_contours
import pytest

def f():
  raise SystemExit(1)

def test_mytest():
  with pytest.raises(SystemExit):
    f()

def test_separate():
