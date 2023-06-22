
import numpy as np

from numba import njit

class Aircraft:
    def __init__(self, max_vel=25, max_accel = 14):
        self.positions = []
        self.velocities = []
        self.accelarations = []
        self.headings = []
        self.active = []
        self.flight_times = []
        self.max_flight_times = []
        
        self.n_ac = 0
        
        self.max_vel = max_vel
        self.max_accel = max_accel
        
        self.updates = 0
    
    def add_ac(self, bounds:(float,float), pos:(float,float)=None, vel:(float,float)=None, accel:(float,float)=None, flight_time_bounds:(float,float)=(10,30)):
        pos = np.random.uniform((0,0), bounds, 2) if pos is None else np.asarray(pos)
        vel = np.random.uniform(-self.max_vel, self.max_vel, 2) if vel is None else np.asarray(vel)
        accel = np.random.uniform(-self.max_accel, self.max_accel,2) if accel is None else np.asarray(accel)
        max_flight_time = np.random.uniform(*flight_time_bounds)

        if self.n_ac == 0:
            self.fresh_aircraft(pos, vel, accel,max_flight_time)
        else:
            self.append_aircraft(pos, vel, accel,max_flight_time)
        self.n_ac+=1

    def append_aircraft(self, pos, vel, accel, max_flight_time):
        self.positions = np.append(self.positions, [pos], axis=0)
        self.velocities = np.append(self.velocities, [vel], axis=0)
        self.accelarations = np.append(self.accelarations,[accel],axis=0)
        self.headings = np.append(self.headings, [np.rad2deg(np.arctan2(vel[1], vel[0]))])
        self.active = np.append(self.active, [True])
        self.flight_times = np.append(self.flight_times, [0.])
        self.max_flight_times = np.append(self.max_flight_times, max_flight_time)

    def fresh_aircraft(self, pos, vel, accel,max_flight_time):
        self.positions = np.array([pos])
        self.velocities = np.array([vel])
        self.accelarations = np.array([accel])
        self.headings = np.array([np.deg2rad(np.arctan2(vel[1], vel[0]))])
        self.active = np.array([True])
        self.flight_times = np.array([0.])
        self.max_flight_times = np.array([max_flight_time])
        
    def update(self, ts, bounds):
        self.flight_times += ts # Update how long the aircraft have been in the air for
        
        # Get the list of active and inactive aircraft
        inactive_idxs = np.array(list(range(len(self.active))))
        active_idxs = np.where(self.flight_times<=self.max_flight_times)[0]
        inactive_idxs = np.setdiff1d(inactive_idxs, active_idxs)
        
        # Update the status of inactive aircraft
        self.active[inactive_idxs] = False
        
        self.positions[active_idxs] += self.velocities[active_idxs]*ts
        self.headings[active_idxs] = np.rad2deg(np.arctan2(self.velocities[[active_idxs],1], self.velocities[[active_idxs],0]))
    
        self.velocities[active_idxs] = np.clip(self.velocities[active_idxs] + (self.accelarations[active_idxs]*ts), -self.max_vel, self.max_vel)
        self.velocities[inactive_idxs,:] = np.array([0.,0.])
        self.accelarations[inactive_idxs,:] = np.array([0.,0.])
        
        self.updates += 1

        if self.updates % 10 == 0:
            idxs = np.where(np.random.rand(len(active_idxs)) > 0.4)[0]
            accel_changes = np.random.uniform(-self.max_accel, self.max_accel, size = (idxs.shape[0],2))
            
            self.accelarations[active_idxs[idxs]] = np.clip(self.accelarations[active_idxs[idxs]]+accel_changes, -self.max_accel, self.max_accel)
        
        self.validate_ac(bounds, active_idxs)
    
    def validate_ac(self, bounds, active_idxs):
        for i in range(2):
            result = active_idxs[np.where(self.positions[active_idxs, i] <= 0)[0]]

            if len(result) > 0:
                self.positions[result,i] = 0
                self.velocities[result,i] *= -0.1
                self.accelarations[result,i] = 0

            result = active_idxs[np.where(self.positions[active_idxs, i] >= bounds[i])[0]]

            if len(result) > 0:
                self.positions[result,i] = bounds[i]
                self.velocities[result,i] *= -0.1
                self.accelarations[result,i] = 0
                
    def __iter__(self):
        return self._iterate_aircraft()

    def _iterate_aircraft(self):
        for position, velocity, heading, accel, active in zip(self.positions, self.velocities, self.headings, self.accelarations,self.active):
            yield [position[0],position[1], velocity[0], velocity[1],heading, accel[0], accel[1], active]
        