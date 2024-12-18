# fusion.py

import time
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

class MovingAverageFilter:
    def __init__(self, window_size=12):
        self.window_size = window_size
        self.values = []

    def apply(self, quaternion):
        self.values.append([quaternion.w, quaternion.x, quaternion.y, quaternion.z])
        if len(self.values) > self.window_size:
            self.values.pop(0)
        avg = [sum(x)/len(self.values) for x in zip(*self.values)]
        return Quaternion(avg[0], avg[1], avg[2], avg[3])

class MadgwickFilter:
    def __init__(self, beta=0.03):
        self.beta = beta
        self.q = Quaternion()
        self.deadband = 0.015
    
    def update(self, gyro, accel, dt):
        gyro = [0.0 if abs(x) < self.deadband else x for x in gyro]
        
        gx = gyro[0] * pi / 45.0
        gy = gyro[1] * pi / 45.0
        gz = gyro[2] * pi / 45.0
        
        norm = sqrt(accel[0]**2 + accel[1]**2 + accel[2]**2)
        if norm < 1e-5:
            return
        ax = accel[0] / norm
        ay = accel[1] / norm
        az = accel[2] / norm
        
        qw, qx, qy, qz = self.q.w, self.q.x, self.q.y, self.q.z
        
        _2qw = 2.0 * qw
        _2qx = 2.0 * qx
        _2qy = 2.0 * qy
        _2qz = 2.0 * qz
        
        f = [
            2.0*(qx*qz - qw*qy) - ax,
            2.0*(qw*qx + qy*qz) - ay,
            2.0*(0.5 - qx*qx - qy*qy) - az
        ]
        
        J = [
            [-_2qy, _2qz, -_2qw, _2qx],
            [_2qx, _2qw, _2qz, _2qy],
            [0.0, -4.0*qx, -4.0*qy, 0.0]
        ]
        
        gradient = [0.0, 0.0, 0.0, 0.0]
        for i in range(3):
            for j in range(4):
                gradient[j] += J[i][j] * f[i]
        
        norm = sqrt(sum(x*x for x in gradient))
        if norm > 0:
            gradient = [x/norm for x in gradient]
        
        rate = dt * (1.0 - self.beta)
        self.q.w += rate * (-qx*gx - qy*gy - qz*gz) - self.beta * gradient[0]
        self.q.x += rate * (qw*gx + qy*gz - qz*gy) - self.beta * gradient[1]
        self.q.y += rate * (qw*gy - qx*gz + qz*gx) - self.beta * gradient[2]
        self.q.z += rate * (qw*gz + qx*gy - qy*gx) - self.beta * gradient[3]
        
        self.q.normalize()
