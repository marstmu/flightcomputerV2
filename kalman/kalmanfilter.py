class KalmanFilter:
    def __init__(self, dt, process_noise, measurement_noise):
        # Time step
        self.dt = dt
        
        # State vector [angle, angular velocity]
        self.x = [[0.0], [0.0]]
        
        # State transition matrix
        self.F = [[1, dt], [0, 1]]
        
        # Measurement matrix
        self.H = [[1, 0]]
        
        # Process noise covariance
        self.Q = [[process_noise, 0], [0, process_noise]]
        
        # Measurement noise covariance
        self.R = [[measurement_noise]]
        
        # Covariance matrix
        self.P = [[1, 0], [0, 1]]
        
    def predict(self):
        # Prediction step
        self.x = self._matrix_mult(self.F, self.x)
        Ft = self._matrix_transpose(self.F)
        self.P = self._matrix_add(
            self._matrix_mult(self.F, self._matrix_mult(self.P, Ft)),
            self.Q
        )

    def update(self, z):
        # Measurement update step
        y = self._matrix_sub(z, self._matrix_mult(self.H, self.x))
        S = self._matrix_add(self._matrix_mult(self.H, self._matrix_mult(self.P, self._matrix_transpose(self.H))), self.R)
        K = self._matrix_mult(self.P, self._matrix_mult(self._matrix_transpose(self.H), [[1 / S[0][0]]]))  # Kalman gain
        self.x = self._matrix_add(self.x, self._matrix_mult(K, y))
        I = [[1, 0], [0, 1]]  # Identity matrix
        self.P = self._matrix_mult(self._matrix_sub(I, self._matrix_mult(K, self.H)), self.P)

    def get_state(self):
        return self.x

    # Helper matrix functions
    def _matrix_add(self, A, B):
        return [[A[i][j] + B[i][j] for j in range(len(A[0]))] for i in range(len(A))]

    def _matrix_sub(self, A, B):
        return [[A[i][j] - B[i][j] for j in range(len(A[0]))] for i in range(len(A))]

    def _matrix_mult(self, A, B):
        return [[sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]

    def _matrix_transpose(self, A):
        return [[A[j][i] for j in range(len(A))] for i in range(len(A[0]))]

