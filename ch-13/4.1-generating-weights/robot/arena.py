"""Represent the lines of the arena"""
try:
  from ulab import numpy as np
except ImportError:
  import numpy as np

width = 1500
height = 1500
cutout_width = 500
cutout_height = 500

low_probability = 10 ** -10

boundary_lines = [
    [(0,0), (0, height)],
    [(0, height), (width, height)],
    [(width, height), (width, cutout_height)],
    [(width, cutout_height), (width - cutout_width, cutout_height)],
    [(width - cutout_width, cutout_height), (width - cutout_width, 0)],
    [(width - cutout_width, 0), (0, 0)],
]

def contains(x, y):
  """Return True if the point is inside the arena.
  if the point is inside the rectangle, but not inside the cutout, it's inside the arena.
  """  
  # is it inside the rectangle?
  if x < 0 or x > width \
    or y < 0 or y > height:
    return False
  # is it inside the cutout?
  if x > (width - cutout_width) and y < cutout_height:
    return False
  return True
