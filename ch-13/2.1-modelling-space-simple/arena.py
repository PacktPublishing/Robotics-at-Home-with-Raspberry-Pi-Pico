"""Represent the lines of the arena"""

width = 1500
height = 1500
cutout_width = 500
cutout_height = 500

boundary_lines = [
    [(0,0), (0, height)],
    [(0, height), (width, height)],
    [(width, height), (width, cutout_height)],
    [(width, cutout_height), (width - cutout_width, cutout_height)],
    [(width - cutout_width, cutout_height), (width - cutout_width, 0)],
    [(width - cutout_width, 0), (0, 0)],
]
