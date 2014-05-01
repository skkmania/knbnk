# -*- coding: utf-8 -*-
#import pytest
import classes.knpage as kp
#import classes.knutil as ku


class TestGraph:
    def test_write_binarized_file(self, graph2):
        knp = kp.KnPage(graph2)
        knp.write_binarized_file()

    def test_write_contours_bounding_rect_to_file(self, graph2):
        knp = kp.KnPage(graph2)
        knp.write_contours_bounding_rect_to_file()


class TestBinarized:
    def test_write_binarized_file(self, kn005):
        knp = kp.KnPage(kn005)
        knp.write_binarized_file()


class TestContours:
    def test_getContours(self, kn005):
        knp = kp.KnPage(kn005)
        knp.getContours()
        assert knp.gray is not None
        assert knp.contours is not None
        assert knp.hierarchy is not None

    def test_getCentroids(self, kn005):
        knp = kp.KnPage(kn005)
        knp.getCentroids()
        assert knp.centroids is not None

    def test_writeContour(self, kn005):
        knp = kp.KnPage(kn005)
        knp.getContours()
        knp.writeContour()
        assert knp.img_of_contours is not None

    def test_write_original_with_contour_file(self, kn005):
        knp = kp.KnPage(kn005)
        knp.write_original_with_contour_file()

    def test_write_original_with_contour_and_rect_file(self, kn005):
        knp = kp.KnPage(kn005)
        knp.write_original_with_contour_and_rect_file()


class TestWriteContoursBoundingRect:
    def test_write_contours_bounding_rect_to_file(self, kn005):
        knp = kp.KnPage(kn005)
        knp.write_contours_bounding_rect_to_file()


class TestCollectedBoxes:
    def test_collect_boxes(self, kn005):
        knp = kp.KnPage(kn005)
        knp.collect_boxes()
        knp.write_collected_boxes_to_file()
        knp.write_original_with_collected_boxes_to_file()


class TestWriteAll:
    def test_write_all(self, kn005):
        knp = kp.KnPage(kn005)
        knp.write_all()
