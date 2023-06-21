import time
from datetime import datetime, timedelta
from math import atan2

import numpy as np

from .aircraft import Aircraft
from .towers import Tower, Tower_List, ring_to


class State:
    def __init__(self, bounds:(float,float), sim_t:float = 0.0):
        self.sim_t = sim_t
        
        
        self.bounds = bounds
        self.aircraft=Aircraft()
        
        self.state_log = []
        
        for _ in range(3):
            self.aircraft.add_ac(self.bounds)
            
        self.log()
        
    def update(self, t_step:float):
        self.sim_t += t_step*1000
        
        self.aircraft.update(t_step, self.bounds)
        
        self.log()
        
    def log(self):
        state = list(self.aircraft)
        self.state_log.append(state)
    
                    


class Environment:
    def __init__(self, bounds:(float,float), grid_centre,sim_t:float = 0.0):
        self.running = False
        self.grid_centre = grid_centre
        
        self.__state = State(bounds, sim_t)
        
        self.towers = self.gen_towers()
        
        
    @property
    def sim_time(self):
        return (datetime(1,1,1)+timedelta(milliseconds=self.__state.sim_t)).strftime("%H:%M:%S.%f")[:-4]
    
    @property
    def state(self):
        return self.__state.aircraft
    
    def gen_towers(self, rings=2, size=200,max_signal=[10]):
        towers = ring_to(self.grid_centre, rings, size, max_signal)
        
        return Tower_List(towers)
        
    def run(self, ts=0.1):
        self.running = True
        
        while self.running:
            
            self.__state.update(ts)
            self.towers.update_towers(self.__state.aircraft)
            
            time.sleep(ts)
         
    
    def stop(self):
        self.running = False
        
        return np.array(self.__state.state_log)
        
    
        
    

        
        