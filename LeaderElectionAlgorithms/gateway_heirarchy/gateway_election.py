import numpy as np
import heapq

def get_gateway_leaders(aircraft, towers, active_aircraft, previous_gateways):
    leaders = []
    
    for i, tower in enumerate(towers.aircraft_list):
        if len(tower) == 0 or not towers.active[i]:
            leaders.append(None)
            continue
        
        valid_candidates = np.intersect1d(tower, active_aircraft)
        
        if len(valid_candidates) == 0:
            leaders.append(None)
            continue

        if previous_gateways[i] in valid_candidates:
            leaders.append(previous_gateways[i])
            continue
        
        dists = np.linalg.norm(aircraft.positions[valid_candidates]-towers.centres[i],axis=1)
        
        leaders.append(valid_candidates[np.argmax(aircraft.heuristics[valid_candidates]-dists)])
    
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
        
        aircraft.accelerations[leader] = vec


        