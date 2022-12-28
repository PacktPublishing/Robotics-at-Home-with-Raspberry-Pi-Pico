class PIDController:
    def __init__(self, kp, ki, kd, d_filter_gain=0.1, imax=None, imin=None):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.d_filter_gain = d_filter_gain
        self.imax = imax
        self.imin = imin
        self.reset()

    def reset(self):
        self.integral = 0
        self.error_prev = 0
        self.derivative = 0

    def calculate(self, error, dt):
        self.integral += error * dt
        if self.imax is not None and self.integral > self.imax:
            self.integral = self.imax
        if self.imin is not None and self.integral < self.imin:
            self.integral = self.imin
        # Add a low pass filter to the difference
        difference = (error - self.error_prev) * self.d_filter_gain
        self.error_prev += difference
        self.derivative = difference / dt

        return self.kp * error + self.ki * self.integral + self.kd * self.derivative
