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


target_zone = [
  [(1100, 900), (1100, 1100)],
  [(1100, 1100), (1250, 1100)],
  [(1250, 1100), (1250, 900)],
  [(1250, 900), (1100, 900)],
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

def point_is_inside_target_zone(point):
  """Return True if the point is inside the target zone"""
  # cheat a little, the target zone is a rectangle.
  # if the point is inside the rectangle, it's inside the target zone.
  if point[0] < 1100 or point[0] > 1250 \
    or point[1] < 900 or point[1] > 1100:
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


def point_near_boundaries(point_x, point_y, distance):
  """Return True if the point is close enough to the boundary lines"""
  for line_segment in boundary_lines:
    if distance_from_line_segment(line_segment, point_x, point_y) < distance:
      return True
  return False
