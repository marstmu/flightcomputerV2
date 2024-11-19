import math

# quaternion math helpers
def quaternion_multiply(q1, q2):
    """multiply two quaternions."""
    w1, x1, y1, z1 = q1
    w2, x2, y2, z2 = q2
    return [
        w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
        w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
        w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
        w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2,
    ]

def normalize_quaternion(q):
    """normalize a quaternion."""
    norm = math.sqrt(sum([i * i for i in q]))
    return [i / norm for i in q]

def quaternion_to_rotation_matrix(q):
    """convert a quaternion to a 3x3 rotation matrix."""
    w, x, y, z = q
    return [
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
    ]

def matrix_vector_multiply(matrix, vector):
    """multiply a 3x3 matrix by a 3x1 vector."""
    return [
        sum(matrix[i][j] * vector[j] for j in range(3))
        for i in range(3)
    ]

def matrix_add(A, B):
    """add two matrices."""
    return [
        [A[i][j] + B[i][j] for j in range(len(A[0]))]
        for i in range(len(A))
    ]

def matrix_scalar_multiply(matrix, scalar):
    """multiply a matrix by a scalar."""
    return [
        [element * scalar for element in row]
        for row in matrix
    ]

def matrix_transpose(matrix):
    """transpose a matrix."""
    return [
        [matrix[j][i] for j in range(len(matrix))]
        for i in range(len(matrix[0]))
    ]

# ukf implementation
class UnscentedKalmanFilter:
    def __init__(self):
        self.q = [1.0, 0.0, 0.0, 0.0]  # initial quaternion
        self.bias = [0.0, 0.0, 0.0]  # gyroscope biases
        self.P = [
            [0.1 if i == j else 0.0 for j in range(6)]
            for i in range(6)
        ]  # initial state covariance matrix (6x6 for [q + bias])

    def predict(self, dt, gyro):
        """prediction step using gyroscope readings."""
        omega = [gyro[i] - self.bias[i] for i in range(3)]
        omega_norm = math.sqrt(sum([w * w for w in omega]))

        if omega_norm > 1e-6:  # avoid division by zero
            sin_term = math.sin(omega_norm * dt / 2) / omega_norm
            delta_q = [
                math.cos(omega_norm * dt / 2),
                sin_term * omega[0],
                sin_term * omega[1],
                sin_term * omega[2]
            ]
        else:
            delta_q = [1.0, 0.0, 0.0, 0.0]  # no rotation

        self.q = quaternion_multiply(self.q, delta_q)
        self.q = normalize_quaternion(self.q)

        # prediction update for covariance (simplified)
        # expand with noise modeling if needed.
        self.P = matrix_add(
            self.P,
            matrix_scalar_multiply(self.P, 0.001)  # simplified process noise
        )

    def update(self, accel, mag):
        """update step using accelerometer and magnetometer readings."""
        # ensure inputs have exactly 3 elements
        if len(accel) != 3 or len(mag) != 3:
            raise ValueError("accelerometer and magnetometer inputs must have 3 elements.")

        # normalize accelerometer and magnetometer vectors
        accel_norm = math.sqrt(sum([a * a for a in accel]))
        mag_norm = math.sqrt(sum([m * m for m in mag]))
        accel = [a / accel_norm for a in accel]
        mag = [m / mag_norm for m in mag]

        # reference vectors in world coordinates
        gravity = [0.0, 0.0, 1.0]
        magnetic_north = [1.0, 0.0, 0.0]

        # compute the rotation matrix from the quaternion
        R = quaternion_to_rotation_matrix(self.q)

        # ensure the rotation matrix is valid
        if len(R) != 3 or any(len(row) != 3 for row in R):
            raise ValueError("rotation matrix must be 3x3.")

        # expected accelerometer and magnetometer readings
        accel_expected = matrix_vector_multiply(R, gravity)
        mag_expected = matrix_vector_multiply(R, magnetic_north)

        # ensure expected vectors have 3 elements
        if len(accel_expected) != 3 or len(mag_expected) != 3:
            raise ValueError("expected vectors must have 3 elements.")

        # compute residuals
        residual_accel = [accel[i] - accel_expected[i] for i in range(3)]
        residual_mag = [mag[i] - mag_expected[i] for i in range(3)]
        residual = residual_accel + residual_mag  # combined residual

        # debugging: print residuals
        print("Residuals:", residual)

        # simplified kalman gain (placeholder)
        K = 0.1  # gain factor for simplicity
        update = [K * r for r in residual]

        # ensure update vector has sufficient length
        if len(update) != 6:
            raise ValueError("update vector must have 6 elements.")

        # update quaternion and bias
        dq = update[:3] + [0.0]  # quaternion update (assuming small-angle approx.)
        self.q = normalize_quaternion([
            self.q[i] + dq[i] for i in range(4)
        ])

        # update bias
        self.bias = [self.bias[i] + update[3 + i] for i in range(3)]

print("Quaternion:", ukf.q)
print("Gyroscope Bias:", ukf.bias)
