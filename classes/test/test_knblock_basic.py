# -*- coding: utf-8 -*-
import pytest
import hamcrest as h
from classes.knpage import KnBlock
from classes.knpage import KnBlockException
from classes.knpage import KnBlockParamsException
from classes.knutil import *

HOME_DIR = '/home/skkmania'
DATA_DIR = HOME_DIR + '/mnt2/workspace/pysrc/knbnk/data/twletters'
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


class TestNew:
    def test_initialize_without_params(self):
        with pytest.raises(KnBlockException) as e:
            KnBlock()
        assert 'params is None' in str(e)

    def test_initialize_with_fname_not_existed(self):
        with pytest.raises(KnBlockParamsException) as e:
        #with pytest.raises(KnBlockException) as e:
            KnBlock(params='not_exist_file')
        assert 'not_exist_file' in str(e)

    def test_initialize_with_imcomplete_param_file(self):
        with pytest.raises(KnBlockParamsException) as e:
            KnBlock(params=DATA_DIR + '/imcomplete_sample.json')
        assert 'must be' in str(e)

    def test_new(self, kn):
        assert kn.img is not None
        assert kn.img.shape != (100, 100, 3)
        assert kn.img.shape == (558, 669, 3)
        assert kn.height == 558
        assert kn.width == 669
        assert kn.depth == 3
        assert kn.gray is not None
        assert kn.binarized is not None

    def test_new_try_hamcrest(self, kn):
        h.assert_that(kn.height, h.equal_to(558))


class TestFileName:
    def test_mkFilename(self, kn):
        name = mkFilename(kn, '_cont')
        expect = DATA_DIR + '/twl_can_50_200_hough_1_2_100_cont.jpg'
        assert name == expect

    def test_write_data_file(self, kn):
        kn.write_data_file(DATA_DIR)


class TestBoundingRect:
    def test_write_contours_bounding_rect_to_file(self, kn):
        kn.write_contours_bounding_rect_to_file(DATA_DIR)

    def test_get_boundingBox(self, kn):
        outer_box = kn.get_boundingBox([box01, box02, box03])
        assert outer_box == (20, 30, 25, 25)
        outer_box = kn.get_boundingBox([box01, box02, box03, box04, box05])
        assert outer_box == (10, 20, 45, 45)

    def test_include(self, kn):
        assert not kn.include(box01, box02)
        assert not kn.include(box01, box03)
        assert not kn.include(box01, box04)
        assert kn.include(box02, box06)


class TestInterSect:
    def test_intersect(self, knp):
        box01 = (20, 30, 10, 10)
        box02 = (25, 35, 15, 15)
        box03 = (35, 45, 10, 10)
        box04 = (35, 20, 20, 20)
        box05 = (10, 45, 20, 20)
        kp = KnBlock(knp)
        assert kp.intersect(box01, box02)
        assert kp.intersect(box01, box03)
        assert not kp.intersect(box01, box03, 0, 0)
        assert kp.intersect(box01, box03)
        assert kp.intersect(box01, box04)
        assert not kp.intersect(box01, box04, 0, 0)
        assert kp.intersect(box01, box05)
        assert not kp.intersect(box01, box05, 0, 0)
        assert kp.intersect(box02, box03)
        assert kp.intersect(box02, box04)
        assert kp.intersect(box02, box05)
        assert kp.intersect(box03, box04)
        assert not kp.intersect(box03, box04, 0, 0)
        assert kp.intersect(box03, box05)
        assert not kp.intersect(box03, box05, 0, 0)
        assert kp.intersect(box04, box05)
        assert not kp.intersect(box04, box05, 0, 0)


class TestSweepInBlockMargin:
    def test_sweep_boxes_in_page_margin(self, kn005):
        kn005.getBoxesAndCentroids()
        kn005.sweep_boxes_in_page_margin()
        kn005.sort_boxes()
        kn005.write_boxes_to_file(fix='_trimed')


class TestSweepIncludedBoxes:
    def test_sweep_included_boxes(self, knp):
        kp = KnBlock(knp)
        result = kp.sweep_included_boxes(
            [box01, box02, box03, box04, box05, box06])
        assert len(result) == 5

    def test_sweep_included_boxes_2(self, kn005):
        kn005.getBoxesAndCentroids()
        kn005.sweep_boxes_in_page_margin()
        kn005.sweep_included_boxes()
        kn005.sort_boxes()
        kn005.write_boxes_to_file(fix='_no_inclusion')


class TestSortBoxes:
    def test_sort_boxes(self, kn005):
        kn005.getBoxesAndCentroids()
        kn005.sort_boxes()
        kn005.write_boxes_to_file(target=[100, 200])


class TestSweepMaverickBoxes:
    def test_sweep_maverick_boxes(self, kn005):
        kn005.getBoxesAndCentroids()
        kn005.sweep_boxes_in_page_margin()
        kn005.sweep_included_boxes()
        kn005.sweep_maverick_boxes()
        kn005.sort_boxes()
        kn005.write_boxes_to_file(fix='_no_mavericks')
        kn005.sweep_maverick_boxes()
        kn005.write_boxes_to_file(fix='_no_mavericks_2')
        kn005.sweep_maverick_boxes()
        kn005.write_boxes_to_file(fix='_no_mavericks_3')


class TestCollectBoxes:
    def test_collect_boxes(self, kn005):
        kn005.getBoxesAndCentroids()
        kn005.collect_boxes()
        kn005.write_collected_boxes_to_file()
        kn005.write_original_with_collected_boxes_to_file()


class TestEstimateCharSize:
    def test_estimate_char_size(self, kn005):
        kn005.getBoxesAndCentroids()
        kn005.collect_boxes()
        kn005.estimate_char_size()


class TestEstimateVerticalLines:
    def test_estimate_vertical_lines(self, kn005):
        kn005.getBoxesAndCentroids()
        kn005.collect_boxes()
        kn005.estimate_char_size()
        kn005.estimate_vertical_lines()


class TestEstimateRotateAngle:
    def test_estimate_rotate_angle(self, kn005):
        kn005.getBoxesAndCentroids()
        kn005.collect_boxes()
        kn005.estimate_char_size()
        kn005.estimate_vertical_lines()
        kn005.estimate_rotate_angle()


class TestRotateImage:
    def test_rotate_image(self, kn005):
        kn005.getBoxesAndCentroids()
        kn005.collect_boxes()
        kn005.estimate_char_size()
        kn005.estimate_vertical_lines()
        kn005.estimate_rotate_angle()
        kn005.rotate_image()
        kn005.write_rotated_img_to_file()


class TestRotateImageManyCase:
    def test_rotate_image_many_case(self, kn005):
        for x in [0.7, 0.75, 0.8, 0.85, 0.9]:
            kn005.estimated_angle = x
            kn005.rotate_image()
            kn005.write_rotated_img_to_file(fix='_%f' % x)
        for x in [0.7, 0.75, 0.8, 0.85, 0.9]:
            kn005.estimated_angle = -1 * x
            kn005.rotate_image()
            kn005.write_rotated_img_to_file(fix='_m%f' % x)


class TestManipulateBoxes:
    def test_get_adj_boxes(self, kn):
        boxes = [box01, box02, box03, box04, box05, box06,
                 box11, box12, box13, box14, box15, box16]
        result = kn.get_adj_boxes(boxes, box01)
        assert list(set(result) -
                    set([box01, box02, box03, box04, box05, box06])) == []

    def test_write_original_with_contour_and_rect_file(self, kn):
        kn.write_original_with_collected_boxes_to_file(DATA_DIR)

    def test_write_boxes_to_file(self, kn):
        kn.getBoxesAndCentroids()
        kn.write_boxes_to_file(DATA_DIR)

#class TestSeparate:
#    def test_separate(self, kn):
#        kn.getBoxesAndCentroids()
#        arr = kn.centroids
#        x = range(1, len(arr))
#        actual = kn.separate(arr, x)
#        assert len(actual) > 0
