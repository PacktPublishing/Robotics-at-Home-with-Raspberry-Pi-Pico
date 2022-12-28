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


def get_scaled_sample_around_mean(mean, scale):
    return mean + (random.uniform(-scale, scale) + random.uniform(-scale, scale)) / 2

rotation_scale = 0.05 * abs(motion_angle) + 0.01 * abs(motion_scale)
translation_scale = 0.05 * abs(motion_scale) + 0.01 * abs(motion_angle)

motion_rotation = np.array([get_scaled_sample_around_mean(motion_angle, rotation_scale) for _ in range(poses.shape[0])])
motion_translation = np.array([get_scaled_sample_around_mean(motion_scale, translation_scale) for _ in range(poses.shape[0])])

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
