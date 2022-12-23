import numpy as np
from matplotlib import pyplot as plt, patches
from robot import arena
import random

fig, ax = plt.subplots()

# for line in arena.boundary_lines:
#     plt.plot([line[0][0], line[1][0]], [line[0][1], line[1][1]], color="black")

poses = np.random.normal([250, 300], [2, 2], size=(200, 2))
ax.scatter(poses[:, 0], poses[:, 1])

# create a line for a motion vector
motion_angle = 30
motion_scale = 300
motion_line = np.array([[250, 300], 
  [motion_scale * np.cos(np.radians(motion_angle)), motion_scale * np.sin(np.radians(motion_angle))]])



triangular_proportion = np.sqrt(6) / 2
def get_triangular_sample(mean, standard_deviation):
    base = triangular_proportion * (random.uniform(-standard_deviation, standard_deviation) + random.uniform(-standard_deviation, standard_deviation))
    return mean + base


motion_rotation = np.array([get_triangular_sample(motion_angle, 15) for _ in range(poses.shape[0])])
motion_translation = np.array([get_triangular_sample(motion_scale, 10) for _ in range(poses.shape[0])])

new_poses = np.zeros_like(poses)
new_poses[:, 0] = poses[:, 0] + motion_translation * np.cos(np.radians(motion_rotation))
new_poses[:, 1] = poses[:, 1] + motion_translation * np.sin(np.radians(motion_rotation))
# new_poses[:, 0] = poses[:, 0] + motion_scale * np.cos(np.radians(motion_angle))
# new_poses[:, 1] = poses[:, 1] + motion_scale * np.sin(np.radians(motion_angle))

ax.scatter(new_poses[:, 0], new_poses[:, 1])

# plot the vector arrow
ax.arrow(*motion_line[0], *motion_line[1], color="red", width=5)

# plot the angles on top
# line from original cluster middle, going east.
ax.plot([250, 250+100], [300, 300], color="black")

angle = patches.Wedge((250, 300), 100, 0, motion_angle, width=20, color=(0.3, 0.3, 0.3, 0.3))
ax.add_patch(angle)
ax.text(370, 330, f"{motion_angle}°", horizontalalignment="center", verticalalignment="center", 
  fontsize="x-large")

plt.show()
