import numpy as np
from .gateway_election import get_gateway_leaders

class Leader_Election:
    def __init__(self, n_towers):
        self.are_leaders = []
        self.are_2IC = [None]*n_towers
    
    def update(self, aircraft, towers):
        active_idxs = np.where(aircraft.active)[0]
        if len(active_idxs) == 0:
            return
        
        
        self.are_2IC = get_gateway_leaders(aircraft, towers, active_idxs, self.are_2IC)