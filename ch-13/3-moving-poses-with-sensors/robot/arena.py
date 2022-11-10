"""Represent the lines and target zone of the arena"""


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

def point_is_inside_arena(point):
  """Return True if the point is inside the arena"""
  # cheat a little, the arena is a rectangle, with a cutout.
  # if the point is inside the rectangle, but not inside the cutout, it's inside the arena.
  # this is far simpler than any line intersection method.
  
  # is it inside the rectangle?
  if point[0] < 0 or point[0] > width \
    or point[1] < 0 or point[1] > height:
    return False
  # is it inside the cutout?
  if point[0] > 1000 and point[1] < 500:
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
