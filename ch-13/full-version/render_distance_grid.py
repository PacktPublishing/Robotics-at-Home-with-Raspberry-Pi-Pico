import arena
from matplotlib import pyplot as plt
import numpy as np

def draw_arena_boundaries(arena):
    for line in arena:
        plt.plot([line[0][0], line[1][0]], [line[0][1], line[1][1]], color="red")

def draw_distance_grid(ax):
  overscan_size = arena.overscan * arena.grid_cell_size

  ax.imshow(
    arena.distance_grid.T, 
    extent = [-overscan_size, arena.width + overscan_size, -overscan_size, arena.height + overscan_size], 
    origin="lower",
    cmap="gray",
    norm="log",
  )

fig, ax = plt.subplots()
draw_arena_boundaries(arena.boundary_lines)
print("Value at 0, 1500 is", arena.get_distance_grid_at_point(0, 1500))
# print("Value at 1000, 500 is", arena.get_distance_grid_at_point(1000, 500))
# print("Value at 500, 1000 is", arena.get_distance_grid_at_point(500, 1000))
# print("Value at 550, 1000 is", arena.get_distance_grid_at_point(550, 1000))
draw_distance_grid(ax)
plt.show()
