import time, sys
from lib.icm42670 import read_who_am_i, configure_sensor, read_accel_data, read_gyro_data, set_accel_scale, set_gyro_scale
from math import sqrt, pi

class Quaternion:
    def __init__(self, w=1.0, x=0.0, y=0.0, z=0.0):
        self.w = w
        self.x = x
        self.y = y
        self.z = z
    
    def __mul__(self, other):
        if isinstance(other, Quaternion):
            w = self.w*other.w - self.x*other.x - self.y*other.y - self.z*other.z
            x = self.w*other.x + self.x*other.w + self.y*other.z - self.z*other.y
            y = self.w*other.y - self.x*other.z + self.y*other.w + self.z*other.x
            z = self.w*other.z + self.x*other.y - self.y*other.x + self.z*other.w
            return Quaternion(w, x, y, z)
        return Quaternion(self.w * other, self.x * other, self.y * other, self.z * other)
    
    def normalize(self):
        norm = sqrt(self.w*self.w + self.x*self.x + self.y*self.y + self.z*self.z)
        if norm > 0:
            self.w /= norm
            self.x /= norm
            self.y /= norm
            self.z /= norm

def update_quaternion(q, gyro, dt):
    gx = gyro[0] * pi / 360.0
    gy = gyro[1] * pi / 360.0
    gz = gyro[2] * pi / 360.0
    
    dq = Quaternion(1.0, gx*dt, gy*dt, gz*dt)
    q_new = q * dq
    q_new.normalize()
    return q_new

def main():
    if read_who_am_i() == 0x67:
        configure_sensor()
        set_accel_scale(3)
        set_gyro_scale(1)
        
        current_quaternion = Quaternion()
        last_time = time.ticks_ms()
        
        while True:
            current_time = time.ticks_ms()
            dt = (current_time - last_time) / 1000.0
            last_time = current_time
            
            gyro = read_gyro_data()
            current_quaternion = update_quaternion(current_quaternion, gyro, dt)
            
            sys.stdout.write("{:.3f},{:.3f},{:.3f},{:.3f}\n".format(
                current_quaternion.w,
                current_quaternion.x,
                current_quaternion.y,
                current_quaternion.z
            ))
            
            time.sleep(0.05)

if __name__ == "__main__":
    main()

