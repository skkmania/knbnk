# -*- coding: utf-8 -*-
#import pytest
#import classes.knpage as kp
#import classes.knutil as ku

DATA_DIR = '/home/skkmania/mnt2/workspace/pysrc/knbnk/data'


class TestGraph:
    def test_write_binarized_file(self, graph):
        graph.write_binarized_file(DATA_DIR)

    def test_write_contours_bounding_rect_to_file(self, graph):
        graph.write_contours_bounding_rect_to_file()

    #def test_write_all(self, graph):
    #    graph.write_all(DATA_DIR)


class TestBinarized:
    def test_write_binarized_file(self, kn005):
        kn005.write_binarized_file(DATA_DIR)


class TestContours:
    def test_getContours(self, kn005):
        kn005.getContours()
        assert kn005.gray is not None
        assert kn005.contours is not None
        assert kn005.hierarchy is not None

    def test_getCentroids(self, kn005):
        kn005.getCentroids()
        assert kn005.centroids is not None

    def test_writeContour(self, kn005):
        kn005.getContours()
        kn005.writeContour()
        assert kn005.img_of_contours is not None

    def test_write_original_with_contour_file(self, kn005):
        kn005.write_original_with_contour_file()

    def test_write_original_with_contour_and_rect_file(self, kn005):
        kn005.write_original_with_contour_and_rect_file()


class TestWriteContoursBoundingRect:
    def test_write_contours_bounding_rect_to_file(self, kn005):
        kn005.write_contours_bounding_rect_to_file()


class TestCollectedBoxes:
    def test_collect_boxes(self, kn005):
        kn005.collect_boxes()
        kn005.write_collected_boxes_to_file()
        kn005.write_original_with_collected_boxes_to_file()


class TestWriteAll:
    def test_write_all(self, kn005):
        kn005.write_all(DATA_DIR)
