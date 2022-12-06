from unittest import TestCase
import math
import arena

class TestArena(TestCase):
  def test_get_ray_distance_to_segment_squared_is_not_none(self):
    """Use an example ray, test we get a distance squared (not none)"""
    ray = (253.415, 85.2855, 0.479889)
    segment = arena.boundary_lines[4]
    distance_squared = arena.get_ray_distance_to_segment_squared(ray, segment)
    self.assertIsNotNone(distance_squared)

  def test_get_distance_squared_for_vertical_ray(self):
    """Make a vertical ray, say at y=1000, x=500, heading=pi/2, and test we get the correct distance squared"""
    ray = (500, 1000, math.pi / 2)
    segment = arena.boundary_lines[1]
    distance_squared = arena.get_ray_distance_to_segment_squared(ray, segment)
    self.assertEqual(distance_squared, 500 ** 2)

  def test_get_distance_squared_for_vertical_with_nearest_segment(self):
    """Make a vertical ray, say at y=1000, x=500, heading=pi/2, and test we get the correct distance squared"""
    ray = (500, 1000, math.pi / 2)
    distance_squared = arena.get_ray_distance_squared_to_nearest_boundary_segment(ray)
    self.assertEqual(distance_squared, 500 ** 2)

  def test_get_distance_squared_for_horizontal_ray(self):
    """Make a horizontal ray, say at y=500, x=1000, heading=0, and test we get the correct distance squared"""
    ray = (500, 250, 0)
    distance_squared = arena.get_ray_distance_squared_to_nearest_boundary_segment(ray)
    self.assertEqual(distance_squared, 500 ** 2)
