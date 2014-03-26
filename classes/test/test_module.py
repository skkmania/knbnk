# -*- coding: utf-8 -*-
# test_module.py の内容
import sys


def setup_function(function):
    print ("setting up %s" % function)


def test_func1():
    assert True


def test_func2():
    print "should be captured."
    a_func()
    assert False


def a_func():
    print "this is dummy."


def test_myoutput(capsys):    # または fd レベルの "capfd" を使う
    print ("hello")
    sys.stderr.write("world\n")
    out, err = capsys.readouterr()
    assert out == "hello\n"
    assert err == "world\n"
    print "next"
    out, err = capsys.readouterr()
    assert out == "next\n"
    print "third"
    sys.stderr.write("error again\n")
    assert False
