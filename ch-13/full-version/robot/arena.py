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

## intention - we can use a distance squared function to avoid the square root, and just square the distance sensor readings too.
def get_ray_distance_to_segment_squared(ray, segment):
  """Return the distance squared from the ray origin to the intersection point along the given ray heading.
  The segments are boundary lines, which will be horizontal or vertical, and have known lengths.
  The ray can have any heading, and will be infinite in length.
  Ray -> (x, y, heading)
  Segment -> ((x1, y1), (x2, y2))
  """
  ray_x, ray_y, ray_heading = ray
  segment_x1, segment_y1 = segment[0]
  segment_x2, segment_y2 = segment[1]
  # if the segment is horizontal, the ray will intersect it at a known y value
  if segment_y1 == segment_y2:
    # if the ray is horizontal, it will never intersect the segment
    if ray_heading == 0:
      return None
    # calculate the x value of the intersection point
    intersection_x = ray_x + (segment_y1 - ray_y) / math.tan(ray_heading)
    # is the intersection point on the segment?
    if intersection_x > max(segment_x1, segment_x2) or intersection_x < min(segment_x1, segment_x2):
      return None
    # calculate the distance from the ray origin to the intersection point
    return (intersection_x - ray_x) ** 2 + (segment_y1 - ray_y) ** 2
  # if the segment is vertical, the ray will intersect it at a known x value
  if segment_x1 == segment_x2:
    # if the ray is vertical, it will never intersect the segment
    if ray_heading == math.pi / 2:
      return None
    # calculate the y value of the intersection point 
    intersection_y = ray_y + (segment_x1 - ray_x) * math.tan(ray_heading)
    # is the intersection point on the segment?
    if intersection_y > max(segment_y1, segment_y2) or intersection_y < min(segment_y1, segment_y2):
      return None
    # calculate the distance from the ray origin to the intersection point
    return (intersection_y - ray_y) ** 2 + (segment_x1 - ray_x) ** 2 
  else:
    raise Exception("Segment is not horizontal or vertical")

def get_ray_distance_squared_to_nearest_boundary_segment(ray):
  """Return the distance from the ray origin to the intersection point along the given ray heading.
  The segments are boundary lines, which will be horizontal or vertical, and have known lengths.
  The ray can have any heading, and will be infinite in length.
  Ray -> (x, y, heading)
  """
  # find the distance to each segment
  distances = []
  for segment in boundary_lines:
    distance_squared = get_ray_distance_to_segment_squared(ray, segment)
    if distance_squared is not None:
      distances.append(distance_squared)
  # return the minimum distance
  if distances:
    return min(distances)
  else:
    return None
