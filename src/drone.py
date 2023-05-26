from src.tower import Tower
from shapely.geometry import Point
import numpy as np

from math import atan2
import time


class Drone:
    def __init__(self, screen_size, max_speed:float = 30, init_pos:(float,float) = None, init_vel:(float,float)=None, init_bat:float = None, max_operating_time:float = 120, active_tower:Tower = None, accel_change_prob:float = 0.2, max_accel:float = 10):
        self.gen_time = time.time_ns() // 1_000_000
        
        self.pos = np.random.uniform((0,0), screen_size, 2) if init_pos is None else init_pos
        self.vel = init_vel if init_vel is not None else np.random.uniform(-max_speed, max_speed,2)
        self.bat = init_bat if init_bat is not None else np.random.uniform(0.5,1)
        self.accel = np.array([0,0])
        self.max_speed = max_speed
        self.max_accel = max_accel
        self.max_operating_time = max_operating_time
        
        self.is_leader = False
        self.is_active = True
        
        self._active_tower = active_tower
        
        self.accel_change_prob = accel_change_prob
        
        self.id = hex(abs(hash(f'{self.gen_time}{max_operating_time}{self.bat}')))
        
        print(self.id, self.gen_time)
    
    @property
    def active_tower(self)->Tower:
        return self._active_tower
    
    def poly(self, r: float):
        h = np.rad2deg(self.heading)
        
        points = []
        
        for i in range(0, 360, 360//3):
            theta = np.deg2rad((i+h)%360)
            
            points.append([self.pos[0]+(r*np.cos(theta)), self.pos[1]+(r*np.sin(theta))])
        return np.array(points)
            
        
    
    @property
    def heading(self):
        return atan2(self.vel[1], self.vel[0])
    
    @active_tower.setter
    def active_tower(self, tower:Tower):
        self._active_tower = tower
    
    @property
    def point(self):
        return Point(self.pos)
    
    def update(self, t_step, screen_size):
        if not self.is_active:
            return
        
        self.pos += self.vel*t_step
        
        self.check_screen_conditions(screen_size)
        
        self.update_speed(t_step)
        self.update_bat(t_step)
        
        
        
    def check_screen_conditions(self, screen_size):
        if self.pos[0] <=0:
            self.pos[0] = 0
            self.vel = -0.5*self.vel[0]
            self.accel[0] = 0
        elif self.pos[0] >= screen_size[0]:
            self.pos[0] = screen_size[0]
            self.vel = -0.5*self.vel[0]
            self.accel[0] = 0
            
        if self.pos[1] <= 0:
            self.pos[1] = 0
            self.vel[1] = -0.5*self.vel[1]
            self.accel[1] = 0
        elif self.pos[1] >= screen_size[1]:
            self.pos[1] = screen_size[1]
            self.vel[1] = -0.5*self.vel[1]
            self.accel[1] = 0
    
    def update_speed(self,t):
        self.vel = np.clip(self.vel + (t*self.accel), -self.max_speed, self.max_speed)
        
        if self.vel[0] in [-self.max_speed, self.max_speed]:
            self.accel[0] = 0
            
        if self.vel[1] in [-self.max_speed, self.max_speed]:
            self.accel[1] = 0
        
        if np.random.rand() <= self.accel_change_prob:
            rand = np.random.uniform(-5,5,2)
            
            self.accel = np.clip(self.accel+(rand), -self.max_accel,self.max_accel)
    
    def update_bat(self,t):
        per_cent =((max(abs(self.vel-self.accel))*t)*0.1)/self.max_operating_time
        
        self.bat = np.clip(self.bat-per_cent,0,1)
        
        if self.bat == 0:
            self.vel -= self.vel
            self.accel -= self.accel
            self.is_active = False