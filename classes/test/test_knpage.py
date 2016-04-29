# -*- coding: utf-8 -*-
import pytest
import unittest
from hamcrest import *

from classes.knpage import KnPage

class TestKnPage(unittest.TestCase):
    HOME_DIR = 'Z:/Users/skkmania'
    DATA_DIR = HOME_DIR + '/knbnk/data'

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

  def test_new_with_params(self):
    fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
    params = self.DATA_DIR + '/twletters_01.json'
    kn = KnPage(fname, params)
    assert kn.img != None
    assert kn.img.shape != (100,100,3)
    #self.assertTupleEqual(kn.img.shape, (100,100,3))
    self.assertTupleEqual(kn.img.shape, (558,669,3))
    self.assertEqual(kn.height, 558)
    self.assertEqual(kn.width, 669)
    self.assertEqual(kn.depth, 3)
    return kn

  def test_read_params(self):
    fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
    kn = KnPage(fname)
    params = self.DATA_DIR + '/twletters_01.json'
    kn.read_params(params)
    assert not kn.parameters == None


  def test_separate(self):
    fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
    kn = KnPage(fname)
    expected = "Hello, World!"
    kn.getContours()
    arr = kn.contours
    x = range(1,len(arr))
    actual = kn.separate(arr, x)

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

  def test_write_with_params(self):
      fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
      params = self.DATA_DIR + '/twletters_01.json'
      kn = KnPage(fname, params)
      kn.write_data_file(self.DATA_DIR)
      kn.write_binarized_file(self.DATA_DIR)
      kn.write_contours_bounding_rect_to_file(self.DATA_DIR)
      kn.write_original_with_contour_file(self.DATA_DIR)
      kn.write_original_with_contour_and_rect_file(self.DATA_DIR)

  def test_write_all(self):
      fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
      for i in range(2,9):
        params = self.DATA_DIR + '/twletters_0' + str(i) + '.json'
        kn = KnPage(fname, params)
        kn.write_all(self.DATA_DIR)

  def test_include(self):
      box1 = (20, 30, 10, 10)
      box2 = (25, 35, 15, 15)
      box3 = (35, 45, 10, 10)
      box4 = (35, 20, 20, 20)
      box5 = (10, 45, 20, 20)
      box6 = (27, 37, 10, 10)
      fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
      kn = KnPage(fname)
      assert not kn.include(box1, box2)
      assert not kn.include(box1, box3)
      assert not kn.include(box1, box4)
      assert kn.include(box2, box6)

  def test_intersect(self):
      box1 = (20, 30, 10, 10)
      box2 = (25, 35, 15, 15)
      box3 = (35, 45, 10, 10)
      box4 = (35, 20, 20, 20)
      box5 = (10, 45, 20, 20)
      fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
      kn = KnPage(fname)
      assert kn.intersect(box1, box2)
      assert kn.intersect(box1, box3)
      assert not kn.intersect(box1, box3, 0, 0)
      assert kn.intersect(box1, box3)
      assert kn.intersect(box1, box4)
      assert not kn.intersect(box1, box4, 0, 0)
      assert kn.intersect(box1, box5)
      assert not kn.intersect(box1, box5, 0, 0)
      assert kn.intersect(box2, box3)
      assert kn.intersect(box2, box4)
      assert kn.intersect(box2, box5)
      assert kn.intersect(box3, box4)
      assert not kn.intersect(box3, box4, 0, 0)
      assert kn.intersect(box3, box5)
      assert not kn.intersect(box3, box5, 0, 0)
      assert kn.intersect(box4, box5)
      assert not kn.intersect(box4, box5, 0, 0)

  def test_get_boundingBox(self):
      box1 = (20, 30, 10, 10)
      box2 = (25, 35, 15, 15)
      box3 = (35, 45, 10, 10)
      box4 = (35, 20, 20, 20)
      box5 = (10, 45, 20, 20)
      fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
      kn = KnPage(fname)
      outer_box = kn.get_boundingBox([box1, box2,box3])
      assert outer_box == (20,30,25,25)
      outer_box = kn.get_boundingBox([box1, box2,box3,box4,box5])
      assert outer_box == (10,20,45,45)

  def test_sweep_included_boxes(self):
      box1 = (20, 30, 10, 10)
      box2 = (25, 35, 15, 15)
      box3 = (35, 45, 10, 10)
      box4 = (35, 20, 20, 20)
      box5 = (10, 45, 20, 20)
      box6 = (27, 37, 10, 10)
      fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
      kn = KnPage(fname)
      result = kn.sweep_included_boxes([box1, box2, box3, box4, box5, box6])
      assert len(result) == 5

  def test_get_adj_boxes(self):
      box01 = (20, 30, 10, 10)
      box02 = (25, 35, 15, 15)
      box03 = (35, 45, 10, 10)
      box04 = (35, 20, 20, 20)
      box05 = (10, 45, 20, 20)
      box06 = (27, 37, 10, 10)
      box11 = (120, 30, 10, 10)
      box12 = (125, 35, 15, 15)
      box13 = (135, 45, 10, 10)
      box14 = (135, 20, 20, 20)
      box15 = (110, 45, 20, 20)
      box16 = (127, 37, 10, 10)
      boxes = [box01,box02,box03,box04,box05,box06, box11,box12,box13,box14,box15,box16]
      fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
      kn = KnPage(fname)
      result = kn.get_adj_boxes(boxes, box01)
      assert list( set(result) - set([box01,box02,box03,box04,box05,box06]) )  == []

  def test_sweep_included_boxes_2(self):
      fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
      kn = KnPage(fname)
      kn.sweep_included_boxes()
      kn.write_boxes_to_file(self.DATA_DIR)

  def test_write_original_with_contour_and_rect_file(self):
      fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
      kn = KnPage(fname)
      kn.write_original_with_collected_boxes_to_file(self.DATA_DIR)

  def test_write_self_boxes_to_file(self):
      fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
      kn = KnPage(fname)
      kn.getCentroids()
      kn.write_self_boxes_to_file(self.DATA_DIR)

  def test_collect_boxes(self):
      fname = '/home/skkmania/workspace/pysrc/knpage/data/twletters.jpg'
      kn = KnPage(fname)
      kn.collect_boxes()
      kn.write_collected_boxes_to_file(self.DATA_DIR)
      kn.write_original_with_collected_boxes_to_file(self.DATA_DIR)
