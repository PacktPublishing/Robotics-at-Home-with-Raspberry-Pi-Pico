from matplotlib import pyplot as plt

from robot import arena

for line in arena.boundary_lines:
    plt.plot([line[0][0], line[1][0]], [line[0][1], line[1][1]], color="black")
overscan_size = arena.overscan * arena.grid_cell_size
plt.imshow(
    arena.distance_grid.T,
    extent = [-overscan_size, arena.width + overscan_size, -overscan_size, arena.height + overscan_size], 
    origin="lower",
    cmap="gray"
)

plt.show()
