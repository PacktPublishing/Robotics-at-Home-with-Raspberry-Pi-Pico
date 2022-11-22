from matplotlib import pyplot as plt
import numpy as np

distribution_size = (2, 500)
uniform_dist = np.random.uniform(low=-1.5, high=1.5, size=distribution_size)
gauss_dist = np.random.normal(loc=0.0, scale=0.5, size=distribution_size)

def prepare_scatter(ax, data):
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_aspect(1)
    ax.scatter(data[0], data[1])
    data_sd = data.std(1)
    data_mean = data.mean(1)
    print(data_mean, data_sd)
    circle = plt.Circle(data_mean, data_sd[0], color='r', fc=(1,0.6,0.6,0.3))
    ax.add_patch(circle)

fig = plt.figure()
gs = fig.add_gridspec(2, 2)
uniform_scatter = fig.add_subplot(gs[0, 0])
gauss_scatter = fig.add_subplot(gs[0, 1])
uniform_hist = fig.add_subplot(gs[1, 0], sharex = uniform_scatter)
gauss_hist = fig.add_subplot(gs[1, 1], sharex = gauss_scatter)
# fig, ((uniform_scatter, gauss_scatter), (uniform_hist, gauss_hist)) = plt.subplots(2, 2)
prepare_scatter(uniform_scatter, uniform_dist)
prepare_scatter(gauss_scatter, gauss_dist)

# Plot the histograms
bins=16
uniform_hist.hist(uniform_dist[0], bins=bins)
gauss_hist.hist(gauss_dist[0], bins=bins)
# fig.tight_layout()

plt.show()
