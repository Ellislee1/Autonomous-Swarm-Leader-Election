import numpy as np
from .gateway_election import get_gateway_leaders, force_update_accelerations
from .leader_election import leader_election
from functools import reduce

class Leader_Election:
    def __init__(self, n_towers, frequency:(int) = 50):
        self.are_leaders = None
        self.are_2IC = [None]*n_towers
        self.update_timer = 0
        self.frequency = frequency
        
        self.logging = []
        self.last_update = -1
    
    def save_log(self, path):
        np.save(path, self.logging)
    
    def log(self, aircraft, towers, sim_t):
        state = []
        
        active_idxs = np.where(aircraft.active)[0]
        for i, ac in enumerate(self.are_2IC):
            local_state = np.array([sim_t, i, ac if ac != None else -1, len(np.intersect1d(towers.aircraft_list[i], active_idxs)),towers.active[i]])
            state.append(local_state)
        
        if self.logging == []:
            self.logging = np.array([state])
        else:
            self.logging = np.append(self.logging, [state], axis=0)
            
        # print(self.logging.shape)
    
    def update(self, aircraft, towers, sim_t):
        
        leader_election(aircraft)

        active_idxs = np.where(aircraft.active)[0]
        if len(active_idxs) == 0:
            return



        update = sim_t % 15 == 0 and sim_t >= 0 and int(sim_t) != self.last_update
        
        self.are_2IC = get_gateway_leaders(
            aircraft,
            towers,
            active_idxs,
            self.are_2IC,
            update
        )
        self.last_update = int(sim_t)

        force_update_accelerations(self.are_2IC, aircraft, towers, active_idxs)

        active_towers = np.where(towers.active)[0]
        in_towers = np.asanyarray(towers.aircraft_list, dtype=object)[active_towers].reshape(-1).tolist() 

        in_towers = reduce(lambda x,y: x+y, in_towers)

        active_idxs = np.intersect1d(in_towers, active_idxs)

        # if self.are_leaders is None or any(
        #     leader not in active_idxs for leader in self.are_leaders
        # ):
        #     try:
        #         ac = aircraft.heuristics[active_idxs]
        #         self.are_leaders = [active_idxs[np.argmax(ac)]]
        #     except:
        #         self.are_leaders = []
            
        # print(self.are_leaders)