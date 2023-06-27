import time
from datetime import datetime, timedelta
from math import atan2

import numpy as np

from .aircraft import Aircraft
from .towers import Tower, Tower_List, ring_to


class State:
    """This holds aircraft state information as well as the sim time
    """
    def __init__(self, bounds:(float,float), sim_t:float = 0.0, N:int = 15):
        self.sim_t = sim_t
        
        self.bounds = bounds # Physical bounds for aircraft to operate in
        self.aircraft=Aircraft() # Instansiate the aircraft object
        
        self.state_log = [] # This will be used to store states of aircraft
        
        for _ in range(N): # Add N aircraft
            self.aircraft.add_ac(self.bounds)
            
        self.log() # Begin the logging
        
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
    
                    


class Environment:
    """This class holds and runs the environment. It is designed to be executed from a child thread from the UI.
    """
    def __init__(self, bounds:(float,float), grid_centre,sim_t:float = 0.0):
        self.running = False # A flag for if the sim is running
        self.grid_centre = grid_centre # The centre coordinates for the middle hex
        
        self.__state = State(bounds, sim_t) # Instantiate the state (aircraft)
        
        self.towers = self.gen_towers() # Generate the towers (generated in a spiral from the centre.)
        
        
    @property # The sim time formatted in Hours:Minutes:Seconds.miliseconds
    def sim_time(self):
        return (datetime(1,1,1)+timedelta(milliseconds=self.__state.sim_t)).strftime("%H:%M:%S.%f")[:-4]
    
    @property # A formatted printout of the state of the aircraft
    def state(self):
        return self.__state.aircraft
    
    def gen_towers(self, rings=3, size=150,max_signal=[10], random_out:int = 0):
        """Generate towers in rings

        Args:
            rings (int, optional): Number of rings to generate. Defaults to 3.
            size (int, optional): How wide the towers are. Defaults to 150.
            max_signal (list, optional): Default starting max signal. Defaults to [10].
            random_out (int, optional): How many towers to initilise as disconnected. 0 is no towers n>0 is the number of towers to drop. -1 is a random number.
        """
        towers = ring_to(self.grid_centre, rings, size, max_signal) # Generate towers to

        
        if random_out > 0: # Set N towers to be inactive
            out_idxs = np.random.choice(range(len(towers)), size = max(random_out, len(towers)))
            for idx in out_idxs:
                towers[idx].acitve = False
        
        elif random_out == -1: # Set a random number of towers to be inactive.
            rand_vals = np.random.rand(len(towers))
            idxs = np.where(rand_vals <=0.3)[0]
            for idx in idxs:
                towers[idx].active = False

        return Tower_List(towers)
        
    def run(self, ts=0.1):
        """The main run loop

        Args:
            ts (float, optional): The time step in seconds. Defaults to 0.1.
        """
        self.running = True # Simulation running flag
        
        while self.running: # Run while the flag is active
            
            self.__state.update(ts) # Update the aircraft environment
            self.towers.update_towers(self.__state.aircraft) # Update the tower environment
            
            time.sleep(ts if ts <=1 else 0.01) # Force a sleep pause
            
            if not any(ac[-1] for ac in self.state):
                self.running = False # Exit the simulation when no aircraft are active
         
    
    def stop(self):
        """Manual stopping of the simulation (for UI version)
        """
        self.running = False
        
        return np.array(self.__state.state_log)
        
    
        
    

        
        