"""Represent the lines of the arena"""
try:
  from ulab import numpy as np
except ImportError:
  import numpy as np

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

def contains(x, y):
  """Return True if the point is inside the arena.
  if the point is inside the rectangle, but not inside the cutout, it's inside the arena.
  """  
  # is it inside the rectangle?
  if x < 0 or x > width \
    or y < 0 or y > height:
    return False
  # is it inside the cutout?
  if x > 1000 and y < 500:
    return False
  return True
