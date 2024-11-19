from ukf import UnscentedKalmanFilter

# Example usage
ukf = UnscentedKalmanFilter()

# Simulated data
dt = 0.01
gyro = [0.01, -0.02, 10]  # Example gyro readings
accel = [0.0, 0.0, 9.81]  # Example accel readings (gravity aligned)
mag = [0.3, 0.4, 0.5]  # Example magnetometer readings

ukf.predict(dt, gyro)
ukf.update(accel, mag)

print("Quaternion:", ukf.q)
print("Gyroscope Bias:", ukf.bias)
