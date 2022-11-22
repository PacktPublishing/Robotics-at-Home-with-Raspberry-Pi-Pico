import random
import math

def get_standard_normal_sample():
    """Using the Marasaglia Polar method"""
    while True:
        u = random.uniform(-1, 1)
        v = random.uniform(-1, 1)
        s = u * u + v * v
        if s >= 1:
            continue
        return u * math.sqrt(-2 * math.log(s) / s)

def get_gaussian_sample(mean, standard_deviation):
    return get_standard_normal_sample() * standard_deviation + mean
