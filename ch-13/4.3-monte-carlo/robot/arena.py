"""Represent the lines of the arena"""
try:
  from ulab import numpy as np
except ImportError:
  import numpy as np

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


grid_cell_size = 50
overscan = 10 # 10 each way


def get_distance_to_segment(x, y, segment):
    """Return the distance from the point to the segment.
    Segment -> ((x1, y1), (x2, y2))
    All segments are horizontal or vertical.
    """
    x1, y1 = segment[0]
    x2, y2 = segment[1]
    # if the segment is horizontal, the point will be closest to the y value of the segment
    if y1 == y2 and x >= min(x1, x2) and x <= max(x1, x2):
        return abs(y - y1)
    # if the segment is vertical, the point will be closest to the x value of the segment
    if x1 == x2 and y >= min(y1, y2) and y <= max(y1, y2):
        return abs(x - x1)
    # the point will be closest to one of the end points
    return np.sqrt(
        min(
            (x - x1) ** 2 + (y - y1) ** 2, 
            (x - x2) ** 2 + (y - y2) ** 2
        )
    )


def get_distance_likelihood(x, y):
    """Return the distance from the point to the nearest segment as a decay function."""
    min_distance = None
    for segment in boundary_lines:
        distance = get_distance_to_segment(x, y, segment)
        if min_distance is None or distance < min_distance:
            min_distance = distance
    return 1.0 / (1 + min_distance/250) ** 2


# beam endpoint model
def make_distance_grid():
    """Take the boundary lines. With and overscan of 10 cells, and grid cell size of 5cm (50mm),
    make a grid of the distance to the nearest boundary line.
    """
    grid = np.zeros((
            width // grid_cell_size + 2 * overscan, 
            height // grid_cell_size + 2 * overscan
        ), dtype=np.float)
    for x in range(grid.shape[0]):
        column_x = x * grid_cell_size - (overscan * grid_cell_size)
        for y in range(grid.shape[1]):
            row_y = y * grid_cell_size - (overscan * grid_cell_size)
            grid[x, y] = get_distance_likelihood(
                column_x, row_y
            )
    return grid

distance_grid = make_distance_grid()

def get_distance_grid_at_point(x, y):
  """Return the distance grid value at the given point."""
  grid_x = int(x // grid_cell_size + overscan)
  grid_y = int(y // grid_cell_size + overscan)
  if grid_x < 0 or grid_x >= distance_grid.shape[0] or grid_y < 0 or grid_y >= distance_grid.shape[1]:
    return 0
  return distance_grid[grid_x, grid_y]
