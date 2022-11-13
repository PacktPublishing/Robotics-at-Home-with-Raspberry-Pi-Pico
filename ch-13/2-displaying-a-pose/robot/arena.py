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
