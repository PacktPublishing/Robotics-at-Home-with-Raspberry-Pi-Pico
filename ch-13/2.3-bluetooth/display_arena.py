from matplotlib import pyplot as plt

from robot import arena

for line in arena.boundary_lines:
    plt.plot([line[0][0], line[1][0]], [line[0][1], line[1][1]], color="black")
plt.show()
