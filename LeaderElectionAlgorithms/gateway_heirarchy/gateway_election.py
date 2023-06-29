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
    
    force_update_accelerations(leaders, aircraft, towers, active_aircraft)
    return leaders

def force_update_accelerations(leaders, aircraft, towers,active_aircraft):
    for tower,leader in enumerate(leaders):
        if leader is None:
            continue
        
        not_active = np.setdiff1d(towers.aircraft_list[tower], active_aircraft)
        active = np.setdiff1d(towers.aircraft_list[tower], not_active)
        
        if len(active)<=1:
            continue
        
        pos = aircraft.positions[leader]
        tower_centre = towers.centres[tower]
        
        vec = np.clip(-(pos-tower_centre),-0.5*aircraft.max_accel, 0.5*aircraft.max_accel)
        
        aircraft.accelarations[leader] = vec
        