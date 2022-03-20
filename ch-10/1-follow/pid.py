class PID:
    def __init__(self, proportional_k, integral_k, differential_k, set_point):
        self.proportional_k = proportional_k
        self.integral_k = integral_k
        self.differential_k = differential_k
        self.set_point = set_point

        self.error_sum = 0
        self.last_value = 0

    def update(self, measurement, time_delta):
        error_value = measurement - self.set_point
        proportional = error_value * self.proportional_k

        # calculate integral
        self.error_sum += error_value * time_delta
        integral = self.error_sum * self.integral_k
        self.last_value = error_value

        differentiated_error = (error_value - self.last_value) / time_delta
        differential = differentiated_error * self.differential_k

        return proportional + integral + differential
