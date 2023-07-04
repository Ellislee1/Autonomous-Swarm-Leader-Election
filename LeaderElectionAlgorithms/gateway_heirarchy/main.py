import numpy as np
from .gateway_election import get_gateway_leaders
from .leader_election import NN_Model
from functools import reduce

class Leader_Election:
    def __init__(self, n_towers, frequency:(int) = 50):
        self.are_leaders = None
        self.are_2IC = [None]*n_towers
        self.update_timer = 0
        self.frequency = frequency
        
        self.model = NN_Model(17)
    
    def update(self, aircraft, towers, sim_time):
        
        active_idxs = np.where(aircraft.active)[0]
        if len(active_idxs) == 0:
            return


        self.are_2IC = get_gateway_leaders(aircraft, towers, active_idxs, self.are_2IC)
        
        active_towers = np.where(towers.active)[0]
        in_towers = np.asanyarray(towers.aircraft_list, dtype=object)[active_towers].reshape(-1).tolist()
        
        in_towers = reduce(lambda x,y: x+y, in_towers)
        
        active_idxs = np.intersect1d(in_towers, active_idxs)
        
        self.model.leader_election(aircraft, towers, active_idxs, active_towers, sim_time)

        if self.are_leaders is None or any(
            leader not in active_idxs for leader in self.are_leaders
        ):
            try:
                ac = aircraft.heuristics[active_idxs]
                self.are_leaders = [active_idxs[np.argmax(ac)]]
            except:
                self.are_leaders = []
            
        # print(self.are_leaders)