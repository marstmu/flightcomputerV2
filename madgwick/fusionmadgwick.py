import math

class Fusion:
    def __init__(self, beta=0.01):
        # Quaternion elements representing the estimated orientation
        self.q = [1.0, 0.0, 0.0, 0.0]
        self.beta = beta  # Algorithm gain

    def update_nomag(self, accel, gyro, dt=0.01):
        ax, ay, az = accel
        gx, gy, gz = gyro
        q1, q2, q3, q4 = self.q

        # Convert gyroscope degrees/sec to radians/sec
        gx, gy, gz = map(lambda x: math.radians(x), (gx, gy, gz))

        # Normalize accelerometer measurement
        norm = math.sqrt(ax * ax + ay * ay + az * az)
        if norm == 0:
            return  # avoid division by zero
        ax /= norm
        ay /= norm
        az /= norm

        # Auxiliary variables to avoid repeated calculations
        _2q1 = 2.0 * q1
        _2q2 = 2.0 * q2
        _2q3 = 2.0 * q3
        _2q4 = 2.0 * q4
        _4q1 = 4.0 * q1
        _4q2 = 4.0 * q2
        _4q3 = 4.0 * q3
        _4q4 = 4.0 * q4
        _8q2 = 8.0 * q2
        _8q3 = 8.0 * q3
        q1q1 = q1 * q1
        q2q2 = q2 * q2
        q3q3 = q3 * q3
        q4q4 = q4 * q4

        # Gradient descent algorithm corrective step
        s1 = _4q1 * q3q3 + _2q3 * ay + _2q4 * az - _4q2 * q2q2 + _4q2 * ax
        s2 = _4q2 * q4q4 - _2q4 * ax + _2q3 * az - _4q1 * q2q2 + _4q1 * ay
        s3 = _4q3 * q4q4 + _2q4 * ay - _4q1 * q3q3 + _4q2 * ax + _2q3 * az
        s4 = _4q4 * q1q1 + _2q1 * ay - _4q4 * q2q2 + _4q3 * az - _2q2 * ax

        # Normalize the step magnitude
        norm = math.sqrt(s1 * s1 + s2 * s2 + s3 * s3 + s4 * s4)
        if norm == 0:
            return  # avoid division by zero
        s1 /= norm
        s2 /= norm
        s3 /= norm
        s4 /= norm

        # Apply feedback step
        qDot1 = 0.5 * (-q2 * gx - q3 * gy - q4 * gz) - self.beta * s1
        qDot2 = 0.5 * (q1 * gx + q3 * gz - q4 * gy) - self.beta * s2
        qDot3 = 0.5 * (q1 * gy - q2 * gz + q4 * gx) - self.beta * s3
        qDot4 = 0.5 * (q1 * gz + q2 * gy - q3 * gx) - self.beta * s4

        # Integrate to yield quaternion
        q1 += qDot1 * dt
        q2 += qDot2 * dt
        q3 += qDot3 * dt
        q4 += qDot4 * dt

        # Normalize quaternion
        norm = math.sqrt(q1 * q1 + q2 * q2 + q3 * q3 + q4 * q4)
        self.q = [q1 / norm, q2 / norm, q3 / norm, q4 / norm]

