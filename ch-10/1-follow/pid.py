class PID:
  def __init__(self, proportional_k, integral_k, differential_k) -> None:
    self.proportional_k = proportional_k    
    self.integral_k = integral_k
    self.differential_k = differential_k

    self.integral = 0
    self.last_value = 0

  def update(self, error_value, time_delta):
    proportional = error_value * self.proportional_k

    self.integral += error_value * time_delta
    integral = self.integral * self.integral_k

    differentiated_error = (error_value - self.last_value) / time_delta
    differential = differentiated_error * self.differential_k

    return proportional + integral + differential
