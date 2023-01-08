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

