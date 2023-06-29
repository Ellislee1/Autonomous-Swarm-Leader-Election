import numpy as np
import heapq

def get_gateway_leaders(aircraft, towers, active_aircraft, previous_gateways):
    leaders = []
    
    for i, tower in enumerate(towers.aircraft_list):
        if len(tower) == 0:
            leaders.append(None)
            continue
        
        not_active = np.setdiff1d(tower, active_aircraft)
        
        if len(not_active) == len(tower):
            leaders.append(None)
            continue
        
        valid_candidates = np.setdiff1d(tower, not_active)
        
        if previous_gateways[i] in valid_candidates:
            leaders.append(previous_gateways[i])
            continue
        
        
        battery_values = -(aircraft.max_flight_times[valid_candidates]-aircraft.flight_times[valid_candidates])
        
        leaders.append(valid_candidates[np.argmin(battery_values)])
    
    return leaders