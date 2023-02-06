import matplotlib.pyplot as plt
import numpy as np
import random

population_size = 100000


def make_uniform_series_plot(n):
    uniform_series = np.array(
        [
            sum(random.uniform(0, 1) for _ in range(n)) / n
            for _ in range(population_size)
        ]
    )
    plt.hist(uniform_series, bins=200, histtype="step", label=f"n={n}")


make_uniform_series_plot(1)
make_uniform_series_plot(2)
make_uniform_series_plot(3)
make_uniform_series_plot(4)
make_uniform_series_plot(8)
make_uniform_series_plot(12)
plt.title(f"Uniform series")

plt.legend()
plt.show()
