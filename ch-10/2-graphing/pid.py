class PID:
  def __init__(self, proportional_k, integral_k, differential_k, set_point):
    self.proportional_k = proportional_k    
    self.integral_k = integral_k
    self.differential_k = differential_k
    self.set_point = set_point

    self.error_sum = 0
    self.last_value = 0
    self.min_output = -1
    self.max_output = 1


  def update(self, measurement, time_delta):
    error_value = measurement - self.set_point
    proportional = error_value * self.proportional_k

    # calculate integral   
    self.error_sum += error_value * time_delta
    # clamp it
    self.error_sum = min(self.max_output, self.error_sum)
    self.error_sum = max(self.min_output, self.error_sum)

    integral = self.error_sum * self.integral_k

    differentiated_error = (error_value - self.last_value) / time_delta
    differential = differentiated_error * self.differential_k

    output = proportional + integral + differential
    # clamp output
    output = min(self.max_output, output)
    output = max(self.min_output, output)

    return output
