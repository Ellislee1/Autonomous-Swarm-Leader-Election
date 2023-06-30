import numpy as np
from .gateway_election import get_gateway_leaders

class Leader_Election:
    def __init__(self, n_towers, frequency:(int) = 50):
        self.are_leaders = None
        self.are_2IC = [None]*n_towers
        self.update_timer = 0
        self.frequency = frequency
    
    def update(self, aircraft, towers, update_interval):
        active_idxs = np.where(aircraft.active)[0]
        if len(active_idxs) == 0:
            return


        self.are_2IC = get_gateway_leaders(aircraft, towers, active_idxs, self.are_2IC)
        
        if self.are_leaders is None or any(
            leader not in active_idxs for leader in self.are_leaders
        ):
            self.are_leaders = [np.random.choice(active_idxs)]