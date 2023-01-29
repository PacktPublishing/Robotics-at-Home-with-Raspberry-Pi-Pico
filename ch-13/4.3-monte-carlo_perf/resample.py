import numpy as np
import random


def resample(weights, sample_count):
    """Return sample_count number of samples from the
    poses, based on the weights array.
    Uses low variance resampling"""
    samples = np.zeros((sample_count, 3))
    interval = np.sum(weights) / sample_count
    shift = random.uniform(0, interval)
    cumulative_weights = weights[0]
    source_index = 0
    for current_index in range(sample_count):
        weight_index = shift + current_index * interval
        while weight_index >= cumulative_weights:
            source_index += 1
            source_index = min(len(weights), source_index)
            cumulative_weights += weights[source_index]
        samples[current_index] = source_index
    if samples.shape[0] != sample_count:
        raise Exception("Sample count mismatch in resample.")
    return samples
