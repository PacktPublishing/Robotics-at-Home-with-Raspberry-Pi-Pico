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

def get_binary_occupancy_grid():
  ## Convert the boundary lines to a grid map
  ## with 50mm resolution
  grid_size = 50
  overscan_in_cells = 5
  grid_width = int(width / grid_size) + 2 * overscan_in_cells
  grid_height = int(height / grid_size) + 2 * overscan_in_cells
  grid = [[0 for x in range(grid_width)] for y in range(grid_height)]
  for scan_line in range(grid_height):
    scan_y = (scan_line - overscan_in_cells) * grid_size
    if scan_y < 0 or scan_y > height:
      grid[scan_line] = [1 for x in range(grid_width)]
      continue
    # For each line, set the left overscan to 1
    # and the right overscan to 1, but account for the cutout
    grid[scan_line][0:overscan_in_cells] = [1 for x in range(overscan_in_cells)]
    if scan_y < 500:
      cutout_start = int(1000 / grid_size)
      grid[scan_line][overscan_in_cells + cutout_start:] = [1 for x in range(grid_width - overscan_in_cells - cutout_start)]
    else:
      grid[scan_line][overscan_in_cells + int(width / grid_size):] = [1 for x in range(grid_width - overscan_in_cells - int(width / grid_size))]

  return grid


target_zone = [
  [(1100, 900), (1100, 1100)],
  [(1100, 1100), (1250, 1100)],
  [(1250, 1100), (1250, 900)],
  [(1250, 900), (1100, 900)],
]
target_zone_middle = (1175, 1000)


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

def heading_for_target_zone_middle(point_x, point_y):
  """Return the heading to the middle of the target zone"""
  # get the heading to the middle of the target zone
  heading = math.atan2(target_zone_middle[1] - point_y, target_zone_middle[0] - point_x)
  # convert to degrees
  heading = math.degrees(heading)
  # convert to compass heading
  heading = 90 - heading
  # convert to 0-360
  if heading < 0:
    heading += 360
  return heading

def distance_to_target_zone_middle(point_x, point_y):
  """Return the distance to the middle of the target zone"""
  return math.sqrt((target_zone_middle[0] - point_x) ** 2 + (target_zone_middle[1] - point_y) ** 2)
