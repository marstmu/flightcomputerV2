import os
import time
from sensor_data_logger import log_data

def create_directory_if_needed(directory):
    try:
        if directory not in os.listdir("/"):
            print(f"Creating directory: {directory}")
            os.mkdir(directory)
    except Exception as e:
        print(f"Error creating directory: {e}")

data_dir = "logs"
create_directory_if_needed(data_dir)

# Create CSV header
log_file = f"{data_dir}/sensor_log.csv"
with open(log_file, "w") as f:
    f.write("elapsed_time,temperature,pressure,accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z,mag_x,mag_y,mag_z\n")

# Main loop
start_time = time.ticks_ms()  # Use ticks_ms for millisecond precision
try:
    while True:
        current_time = time.ticks_ms()
        elapsed_time = time.ticks_diff(current_time, start_time) / 1000  # Convert to seconds with millisecond precision
        log_data(elapsed_time, data_dir)
        time.sleep(0.1)  # Adjust as needed
except KeyboardInterrupt:
    print("Logging stopped.")

