
import numpy as np

class Aircraft:
    """Thre aircraft class holds information on the state of the aircraft.
    """
    def __init__(self, max_vel=25, max_accel = 18, scale = 1):
        # Initilise the values to record
        self.scale = scale
        self.positions = []
        self.velocities = []
        self.accelerations = []
        self.headings = []
        self.active = []
        self.flight_times = []
        self.max_flight_times = []
        self.heuristics = []
        self.position_error = []
        self.waypoints = []
        
        self.prev_error = []
        self.integral_error = []
        
        self.kp = 0.1  # Proportional gain
        self.ki = 0.01  # Integral gain
        self.kd = 0.1 
        
        self.n_ac = 0 # The number of aircraft in the sim
        self.active_ac = 0 # The active number of aircraft
        
        self.max_vel = max_vel
        self.max_accel = max_accel
        
        self.updates = 0 # Howmany updates have occured
        
        self.flight_time_bounds = (300,900)
        self.t_step = 0
    
    def add_ac(self, bounds:(float,float), pos:(float,float)=None, vel:(float,float)=None, accel:(float,float)=None):
        """Add an aircraft to the environment with either predefined vars or randomly generated is None.
        """
        
        # Check if vars are pre existing
        self.bounds = bounds
        pos = np.random.uniform((0,0), bounds, 2) if pos is None else np.asarray(pos)
        vel = np.random.uniform(-self.max_vel, self.max_vel, 2) if vel is None else np.asarray(vel)
        accel = np.random.uniform(-self.max_accel, self.max_accel,2) if accel is None else np.asarray(accel)
        # max_flight_time = np.random.uniform(*self.flight_time_bounds)
        max_flight_time = np.clip(np.random.normal(7,2)*100, *self.flight_time_bounds)

        # Append aircraft to the state storers
        if self.n_ac == 0:
            self.fresh_aircraft(pos, vel, accel,max_flight_time)
        else:
            self.append_aircraft(pos, vel, accel,max_flight_time)
        self.n_ac+=1
        self.active_ac += 1

    def append_aircraft(self, pos, vel, accel, max_flight_time):
        """This function appends the aircraft to already occupied arrays
        """
        self.positions = np.append(self.positions, [pos], axis=0)
        self.position_error = np.append(self.position_error, [np.random.normal(loc = pos, scale=2.25, size=pos.shape)], axis=0)
        self.velocities = np.append(self.velocities, [vel], axis=0)
        self.accelerations = np.append(self.accelerations,[accel],axis=0)
        self.headings = np.append(self.headings, [np.rad2deg(np.arctan2(vel[1], vel[0]))])
        self.active = np.append(self.active, [True])
        self.flight_times = np.append(self.flight_times, [0.])
        self.max_flight_times = np.append(self.max_flight_times, max_flight_time)
        self.heuristics = np.append(self.heuristics, [0])
        self.waypoints = np.append(self.waypoints, np.random.randint((0,0),self.bounds, (1,2)), axis=0)
        self.prev_error = np.append(self.prev_error, np.zeros((1,2)),axis=0)
        self.integral_error = np.append(self.integral_error, np.zeros((1,2)),axis=0)

    def fresh_aircraft(self, pos, vel, accel,max_flight_time):
        """This function instantiates new state storers and then appends an aircraft
        """
        self.positions = np.array([pos])
        self.position_error = np.array([np.random.normal(loc = pos, scale=2.25, size=pos.shape)])
        self.velocities = np.array([vel])
        self.accelerations = np.array([accel])
        self.headings = np.array([np.deg2rad(np.arctan2(vel[1], vel[0]))])
        self.active = np.array([True])
        self.flight_times = np.array([0.])
        self.max_flight_times = np.array([max_flight_time])
        self.heuristics = np.array([0])
        self.waypoints = np.random.randint((0,0),self.bounds, (1,2))
        self.prev_error = np.zeros((1,2))
        self.integral_error = np.zeros((1,2))
        
        
    def update(self, ts, bounds):
        """Update the environment
        """

        self.t_step += ts
        val = (np.sum(np.abs(self.accelerations), axis=1)/(self.max_accel**2))/10
        
        # self.flight_times += np.clip(ts+ 1/(np.sum(np.abs(self.accelerations), axis=1))**2, ts, ts*3)
        cI = self.max_flight_times/self.flight_time_bounds[-1]
        # print(cI)
        delta = -np.log(0.01/1)/self.flight_time_bounds[-1]
        # delta = 5e-2
        cR = np.random.normal(cI * np.exp(-delta*self.t_step*((np.sqrt(self.accelerations[:,0]**2+self.accelerations[:,1]**2)/self.max_accel)+1)),0.01)
        # print(cI,cR)
        
        self.flight_times = self.max_flight_times - self.flight_time_bounds[-1]*cR
        # print(self.flight_times, self.max_flight_times)
        # self.max_flight_times
        self.flight_times[cR <= 0.05] = self.max_flight_times[cR <= 0.05]+1
        self.flight_times[self.active == False] = self.max_flight_times[self.active == False]+1
        
        # self.flight_times = self.max_flight_times - (self.max_flight_times*np.exp(self.t_step*(np.log(1/self.max_flight_times)/self.max_flight_times)*((np.sqrt(self.accelerations[:,0]**2+self.accelerations[:,1]**2)/self.max_accel)+1)))
        # self.flight_times[self.flight_times>= self.max_flight_times*0.9] = np.inf
        # print(self.flight_times, self.max_flight_times*0.9)
        # self.flight_times += ts
        
        
        # Get the list of active and inactive aircraft
        inactive_idxs = np.array(list(range(len(self.active))))
        active_idxs = np.where(self.flight_times<=self.max_flight_times)[0]
        inactive_idxs = np.setdiff1d(inactive_idxs, active_idxs)
        
        # self.update_waypoints()
        self.calculate_acceleration(ts)
        
        # Update the status of inactive aircraft
        self.active[inactive_idxs] = False
        self.active_ac = len(np.where(self.active)[0])
        
        # Update the positions and headings
        self.positions[active_idxs] += (self.scale*self.velocities[active_idxs])*ts
        self.position_error = np.random.normal(loc = self.positions, scale=3, size = self.positions.shape)
        self.headings[active_idxs] = np.rad2deg(np.arctan2(self.velocities[[active_idxs],1], self.velocities[[active_idxs],0]))

        # Update the velocity and accel randomly
        self.velocities[active_idxs] = np.clip(self.velocities[active_idxs] + (self.accelerations[active_idxs]*ts), -self.max_vel, self.max_vel)
        self.velocities[inactive_idxs,:] = np.array([0.,0.])
        self.accelerations[inactive_idxs,:] = np.array([0.,0.])
        
        self.updates += 1

        # Set the new accelerations
        # if self.updates % 10 == 0:
        #     idxs = np.where(np.random.rand(len(active_idxs)) > 0.4)[0]
        #     accel_changes = np.random.uniform(-self.max_accel, self.max_accel, size = (idxs.shape[0],2))
            
        #     self.accelerations[active_idxs[idxs]] = np.clip(self.accelerations[active_idxs[idxs]]+accel_changes, -self.max_accel, self.max_accel)
        
        self.validate_ac(bounds, active_idxs) # Make sure aircraft dont leave the environment
        
        self.update_heuristics(ts)
        
        # print(self.updates, self.t_step,self.active, 'HERE')
    
    # def update_waypoints(self):
    #     dist = np.linalg.norm(self.positions-self.waypoints, axis=-1)
        
    #     update = np.where(dist <= 10)[0]
        
    #     new_waypoints = np.random.randint((0,0),self.bounds, (len(update),2))
        
    #     self.waypoints[update] = new_waypoints
    
    def calculate_acceleration(self, time_step):
        # Calculate position error for each aircraft
        error = self.waypoints - self.positions
        
        # Calculate direction vector from aircraft to waypoint
        sub = np.linalg.norm(error, axis=1)[:, np.newaxis]

        direction_vector = error / sub
        
    
        
        # Calculate desired velocity vector towards the waypoint
        desired_velocity = direction_vector * self.max_vel
        
        # Calculate acceleration needed to reach desired velocity
        self.accelerations = (desired_velocity - self.velocities) / time_step
    
        
        # Clip acceleration to maximum allowed value for each aircraft
        self.accelerations = np.clip(self.accelerations, -self.max_accel, self.max_accel)*(0.25*(time_step/(1/30)))


    
    def validate_ac(self, bounds, active_idxs):
        """Validate the states of the aircraft
        """
        for i in range(2):
            result = active_idxs[np.where(self.positions[active_idxs, i] <= 0)[0]]
            

            if len(result) > 0:
                self.positions[result,i] = 0
                self.velocities[result,i] *= -0.1
                self.accelerations[result,i] = 0

            result = active_idxs[np.where(self.positions[active_idxs, i] >= bounds[i])[0]]

            if len(result) > 0:
                self.positions[result,i] = bounds[i]
                self.velocities[result,i] *= -0.1
                self.accelerations[result,i] = 0
    
    def update_heuristics(self, ts):
        self.heuristics = np.clip((self.max_flight_times-self.flight_times),0, np.inf)

    
    def __iter__(self):
        return self._iterate_aircraft()

    def _iterate_aircraft(self):
        for position, velocity, heading, accel, flight_times, max_flight_times, position_error, active in zip(self.positions, self.velocities, self.headings, self.accelerations, self.flight_times, self.max_flight_times, self.position_error, self.active):
            yield [position[0],position[1], velocity[0], velocity[1],heading, accel[0], accel[1], flight_times, max_flight_times, position_error, active]
        


