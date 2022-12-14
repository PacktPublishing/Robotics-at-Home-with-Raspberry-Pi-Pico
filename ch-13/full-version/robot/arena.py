"""Represent the lines and target zone of the arena"""
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

# need to state clearly the orientation of the heading
# if coordinates 0, 0 is bottom left, then heading 0 is right, with heading increasing anticlockwise.

def point_is_inside_arena(x, y):
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

def get_point_distance_to_segment(x, y, segment):
  """Return the distance squared from the point to the segment.
  Segment -> ((x1, y1), (x2, y2))
  All segments are horizontal or vertical.
  """
  segment_x1, segment_y1 = segment[0]
  segment_x2, segment_y2 = segment[1]
  # if the segment is horizontal, the point will be closest to the y value of the segment
  if segment_y1 == segment_y2 and x >= min(segment_x1, segment_x2) and x <= max(segment_x1, segment_x2):
      return abs(y - segment_y1)
  # if the segment is vertical, the point will be closest to the x value of the segment
  if segment_x1 == segment_x2 and y >= min(segment_y1, segment_y2) and y <= max(segment_y1, segment_y2):
      return abs(x - segment_x1)
  # the point will be closest to one of the end points
  return np.sqrt(min((x - segment_x1) ** 2 + (y - segment_y1) ** 2, (x - segment_x2) ** 2 + (y - segment_y2) ** 2))


def get_point_decay_from_nearest_segment(segments, x, y):
  """Return the distance from the point to the nearest segment as a decay function."""
  max_decay = None
  for segment in segments:
    decay = 1.0 / max(1, get_point_distance_to_segment(x, y, segment))
    if max_decay is None or decay > max_decay:
      max_decay = decay
  return max_decay


grid_cell_size = 50
overscan = 10 # 10 each way

# beam endpoint model
def make_distance_grid():
  """Take the boundary lines. With and overscan of 10 cells, and grid cell size of 5cm (50mm),
  make a grid of the distance to the nearest boundary line.
  """
  grid = np.zeros((width // grid_cell_size + 2 * overscan, height // grid_cell_size + 2 * overscan), dtype=np.float)
  for x in range(grid.shape[0]):
    column_x = x * grid_cell_size - (overscan * grid_cell_size)
    for y in range(grid.shape[1]):
      value = get_point_decay_from_nearest_segment(boundary_lines, column_x, y * grid_cell_size - (overscan * grid_cell_size))
      grid[x, y] = value
  return grid

distance_grid = make_distance_grid()

def get_distance_grid_at_point(x, y):
  """Return the distance grid value at the given point."""
  grid_x = int(x // grid_cell_size + overscan)
  grid_y = int(y // grid_cell_size + overscan)
  if grid_x < 0 or grid_x >= distance_grid.shape[0] or grid_y < 0 or grid_y >= distance_grid.shape[1]:
    return 0
  return distance_grid[grid_x, grid_y]
