"""Represent the lines and target zone of the arena"""
import math

boundary_lines = [
    [(0,0), (0, 1500)],
    [(0, 1500), (1500, 1500)],
    [(1500, 1500), (1500, 500)],
    [(1500, 500), (1000, 500)],
    [(1000, 500), (1000, 0)],
    [(1000, 0), (0, 0)],
]

width = 1500
height = 1500


def point_is_inside_arena(x, y):
  """Return True if the point is inside the arena"""
  # cheat a little, the arena is a rectangle, with a cutout.
  # if the point is inside the rectangle, but not inside the cutout, it's inside the arena.
  # this is far simpler than any line intersection method.
  
  # is it inside the rectangle?
  if x < 0 or x > width \
    or y < 0 or y > height:
    return False
  # is it inside the cutout?
  if x > 1000 and y < 500:
    return False
  return True


def distance_from_line_segment(line_segment, point_x, point_y):
  """Return the distance from the point to the line segment"""
  # get the line as a, b, c where ax + by + c = 0
  line_x1, line_y1 = line_segment[0]
  line_x2, line_y2 = line_segment[1]
  a = line_y1 - line_y2
  b = line_x2 - line_x1
  c = line_x1 * line_y2 - line_x2 * line_y1
  # calculate the distance
  return abs(a * point_x + b * point_y + c) / math.sqrt(a * a + b * b)


# def intersect_ray_with_line_segment(line_segment, ray_x, ray_y, ray_heading):
#   """Return the distance from the ray origin to the intersection point along the given ray heading"""
#   # get the line as a, b, c where ax + by + c = 0
#   line_x1, line_y1 = line_segment[0]
#   line_x2, line_y2 = line_segment[1]
#   a = line_y1 - line_y2
#   b = line_x2 - line_x1
#   c = line_x1 * line_y2 - line_x2 * line_y1
#   # calculate the intersection point

def intersection_distance_for_segment_and_ray(line_segment, ray_as_points):
  """Return the intersection distance of a ray with a line segment, or None if they don't intersect"""
  # get the lines as a, b, c where ax + by + c = 0
  line_x1, line_y1 = line_segment[0]
  line_x2, line_y2 = line_segment[1]
  a = line_y1 - line_y2
  b = line_x2 - line_x1
  c = line_x1 * line_y2 - line_x2 * line_y1
  ray_ox, ray_oy = ray_as_points[0]
  ray_x2, ray_y2 = ray_as_points[1]
  d = ray_oy - ray_y2
  e = ray_x2 - ray_ox
  f = ray_ox * ray_y2 - ray_x2 * ray_oy
  # calculate the intersection point
  denominator = a * e - b * d
  if denominator == 0:
    # the lines are parallel
    return None
  x = (c * e - b * f) / denominator
  y = (a * f - c * d) / denominator
  # check that the intersection point is on both line segments
  if x < min(line_segment[0][0], line_segment[1][0]) \
    or x > max(line_segment[0][0], line_segment[1][0]) \
    or y < min(line_segment[0][1], line_segment[1][1]) \
    or y > max(line_segment[0][1], line_segment[1][1]):
    return None
  # calculate the distance from the ray origin to the intersection point
  dx = x - ray_ox
  dy = y - ray_oy

  return math.sqrt(dx * dx + dy * dy)
  




def point_near_boundaries(point_x, point_y, distance):
  """Return True if the point is close enough to the boundary lines"""
  for line_segment in boundary_lines:
    if distance_from_line_segment(line_segment, point_x, point_y) < distance:
      return True
  return False
