# -*- coding: utf-8 -*-
import pytest
import unittest
from hamcrest import *

from classes.knpage import KnPage

class TestKnPage(unittest.TestCase):

  DATA_DIR = '/home/skkmania/mnt2/workspace/pysrc/knbnk/data'

  # @pytest.fixture
  def test_new(self):
    fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
    kn = KnPage(fname)
    assert kn.img != None
    assert kn.img.shape != (100,100,3)
    #self.assertTupleEqual(kn.img.shape, (100,100,3))
    self.assertTupleEqual(kn.img.shape, (558,669,3))
    self.assertEqual(kn.height, 558)
    self.assertEqual(kn.width, 669)
    self.assertEqual(kn.depth, 3)
    return kn

  @pytest.fixture
  def test_separate(self, newimg):
    expected = "Hello, World!"
    arr = newimg.getContours()[0]
    x = range(1,len(arr))
    actual = newimg.separate(arr, x)

    assert_that(actual, equal_to(expected))
    # PyHamcrest を使わずに assert する場合は以下のように書く
    assert actual == expected
 
  def test_divide(self):
    fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
    kn = KnPage(fname)
    kn.divide()
    assert kn.left == kn.right

  #@pytest.fixture
  #def test_write(self, tmpdir):
  def test_write(self):
      #dataDirectory = tmpdir.mkdir('data')
      #sampleFile = dataDirectory.join("sample.jpeg")
      fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
      kn = KnPage(fname)
      #kn.write(sampleFile)
      kn.write("/tmp/outfile.jpeg")

  def test_getContours(self):
      fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
      kn = KnPage(fname)
      kn.getContours()
      assert kn.gray != None
      assert kn.contours != None
      assert kn.hierarchy != None

  def test_getCentroids(self):
      fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
      kn = KnPage(fname)
      kn.getCentroids()
      assert kn.centroids != None

  def test_writeContour(self):
      fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
      kn = KnPage(fname)
      kn.getContours()
      kn.writeContour()
      assert kn.img_of_contours != None

  def test_mkFilename(self):
      fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
      kn = KnPage(fname)
      name = kn.mkFilename('_cont')
      assert name == '/home/skkmania/workspace/pysrc/knpage/data/twletters_cont.jpg'
      name = kn.mkFilename('_cont',self.DATA_DIR)
      assert name == '/home/skkmania/mnt2/workspace/pysrc/knbnk/data/twletters_cont.jpg'

  def test_write_contours_bounding_rect_to_file(self):
      fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
      kn = KnPage(fname)
      kn.write_contours_bounding_rect_to_file(self.DATA_DIR)

  def test_write_data_file(self):
      fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
      kn = KnPage(fname)
      kn.write_data_file(self.DATA_DIR)

  def test_write_original_with_contour_file(self):
      fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
      kn = KnPage(fname)
      kn.write_original_with_contour_file(self.DATA_DIR)

      
  def test_write_binarized_file(self):
      fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
      kn = KnPage(fname)
      kn.write_binarized_file(self.DATA_DIR)


  def test_write_original_with_contour_and_rect_file(self):
      fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
      kn = KnPage(fname)
      kn.write_original_with_contour_and_rect_file(self.DATA_DIR)
