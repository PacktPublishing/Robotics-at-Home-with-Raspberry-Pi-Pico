from matplotlib import pyplot as plt
import numpy as np

m  = 250

def decay_fn(x):
    return 1.0 / (1 + (abs(x) / m) ** 2)

x = np.arange(0, 1500)
y = np.array([decay_fn(i) for i in x])
plt.plot(x, y)

# plot y=zero line in black
plt.plot([0, 1500], (0, 0), color="black")

# plot x=zero line in red
plt.plot((0, 0), [0, 1], color="black")


# plot the standard deviation of the decay function
# std_dev = np.std(x)
# print(std_dev)
# plt.plot((std_dev, std_dev), [0, 1], color="yellow", linestyle="--")

# plot m line in dashed blue
plt.plot((m, m), [0, 1], color="red", linestyle="--")


plt.show()
