from unittest import TestCase
import math
import arena

class TestArena(TestCase):
  def test_get_point_to_distance_segment_1(self):
      segment = ((0, 0), (0, 1500))
      for x in range(0, 1500):
        for y in (0, 500, 1000):
          self.assertEqual(arena.get_point_distance_to_segment(x, y, segment), x)

  def test_get_point_to_distance_segment_2(self):
      segment = ((0, 0), (1500, 0))
      for y in range(0, 1500):
        for x in (0, 500, 1000):
          self.assertEqual(arena.get_point_distance_to_segment(x, y, segment), y)

  def test_get_point_distance_to_nearest_segment(self):
      segments = [
        [(0, 1500), (1500, 1500)],
      ]
      for y in range(1500):
        for x in (0, 500, 1000):
          self.assertEqual(arena.get_point_distance_to_nearest_segment(segments, x, y), 1500 - y)
