class LPF:
  """Low pass filter."""
  def __init__(self, alpha):
    self.alpha = alpha
    self.last = 0
  def update(self, value):
    self.last = self.alpha * value + (1 - self.alpha) * self.last
    return self.last
