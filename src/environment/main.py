import time
from datetime import datetime, timedelta
from math import atan2

import numpy as np

from .aircraft import Aircraft
from .towers import Towers
from .tasks import TaskManager
from src.logging import Logger
from LeaderElectionAlgorithms import Gateway_Heirarchy


class State:
    """This holds aircraft state information as well as the sim time
    """
    def __init__(self, bounds:(float,float), sim_t:float = 0.0, N:int = 30):
        self.sim_t = sim_t
        self.ts = 0.01
        
        self.bounds = bounds # Physical bounds for aircraft to operate in
        self.aircraft=Aircraft() # Instansiate the aircraft object
        
        self.state_log = [] # This will be used to store states of aircraft
        
        for _ in range(N): # Add N aircraft
            self.aircraft.add_ac(self.bounds)
            
        self.log() # Begin the logging
        
    @property
    def active_ac(self):
        return self.aircraft.active_ac
        
    def update(self, t_step:float):
        """Update the aircraft states with a timestep of t seconds

        Args:
            t_step (float): The time step in seconds
        """
        self.sim_t += t_step*1000 # Convert the time step from seconds into milliseconds
        
        self.aircraft.update(t_step, self.bounds) # Update all the aircraft
        
        self.log() # Log the new states
        
    def log(self):
        """Log the aircraft states
        """
        state = list(self.aircraft) # The environment states is over all aircraft
        self.state_log.append(state) # append this log to the state_log
        
    def reset(self, sim_t, N):
        self.sim_t = sim_t
        self.aircraft=Aircraft() # Instansiate the aircraft object
        
        self.state_log = []
         
        for _ in range(N): # Add N aircraft
            self.aircraft.add_ac(self.bounds)
            
        self.log() # Begin the logging
    
                    


class Environment:
    """This class holds and runs the environment. It is designed to be executed from a child thread from the UI.
    """
    def __init__(self, bounds:(float,float), grid_centre,sim_t:float = 0.0, n_tasks = 5):
        self.running = False # A flag for if the sim is running
        self.grid_centre = grid_centre # The centre coordinates for the middle hex
        
        self.__state = State(bounds, sim_t) # Instantiate the state (aircraft)
        
        self.towers = self.gen_towers(random_out=0) # Generate the towers (generated in a spiral from the centre.)
        self.task_manager = TaskManager(bounds, self.towers, n_tasks)
        self.leader_election = Gateway_Heirarchy(self.towers.n_towers)
        self.start_time = 0
        self.logger = Logger()
        self.sim_run = 0
        self.max_batches = 0
        self.t_delta = time.perf_counter()
        
        self.bounds = bounds
        
        
    @property # The sim time formatted in Hours:Minutes:Seconds.miliseconds
    def sim_time(self):
        return (datetime(1,1,1)+timedelta(milliseconds=self.__state.sim_t)).strftime("%H:%M:%S.%f")[:-4]
    
    @property
    def scale(self):
        return self.state.scale
    
    @property
    def active_ac(self):
        return self.state.active_ac
    
    @property # A formatted printout of the state of the aircraft
    def state(self):
        return self.__state.aircraft
    
    @property
    def log(self):
        return self.__state.state_log
    
    def gen_towers(self, rings=3, size=200, max_signal=[10], random_out:int = -1):
       towers = Towers(size)
       
       towers.gen_rings(self.grid_centre, rings, max_signal)
       
       idxs = np.where(np.random.rand(len(towers.active))<0.3)[0]
       
       towers.active[idxs] = False
       
       return towers
   
    def run_n (self, n = 5, ts = 0.01, N=30, n_tasks=5, path='out/basic', seed = None):
        self.max_batches = n
        self.t_delta = time.perf_counter()
        for _ in range(n):
            self.sim_run+=1
            self.reset(N, n_tasks, seed = seed)
            self.run(ts)
            self.leader_election.save_log(f'{path}_run{self.sim_run}.npy')
            
            
        
    def run(self, ts=0.01):
        """The main run loop

        Args:
            ts (float, optional): The time step in seconds. Defaults to 0.1.
        """
        self.ts = ts
        self.running = True # Simulation running flag
        self.start_time = time.perf_counter()
        update_counter = 0
        sim_t = 0

        while self.running: # Run while the flag is active
            s = time.perf_counter()

            # if update_counter % 60 == 0:
            self.__state.update(ts) # Update the aircraft environment
            self.towers.update_towers(self.__state.aircraft) # Update the tower environment
            self.task_manager.update(round(update_counter*self.ts,2), self.towers, self.__state, round(self.__state.sim_t/1000,2), self.ts)
            self.leader_election.update(self.__state.aircraft, self.towers, np.floor(self.__state.sim_t/1000))
            
            self.logger.log_towers(self.towers)
            self.leader_election.log(self.__state.aircraft, self.towers, np.floor(self.__state.sim_t/1000))

            update_counter += 1
            sim_t = update_counter*self.ts

            if not any(ac[-1] for ac in self.state):
                self.running = False # Exit the simulation when no aircraft are active
    
    def stop(self):
        """Manual stopping of the simulation (for UI version)
        """
        self.running = False
        
        return np.array(self.__state.state_log)
    
    def reset(self, N=30, n_tasks=5, seed = None):
        if seed is not None:
            np.random.seed(seed)
        
        
        self.__state.reset(0, N)
        self.towers = self.gen_towers(random_out=0) # Generate the towers (generated in a spiral from the centre.)
        self.task_manager = TaskManager(self.bounds, self.towers, n_tasks)
        self.leader_election = Gateway_Heirarchy(self.towers.n_towers)
        self.start_time = 0
        self.logger = Logger()
    
        
    
        
    

        
        