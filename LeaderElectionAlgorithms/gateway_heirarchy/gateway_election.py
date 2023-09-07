import numpy as np
import heapq

def get_heuristics(towers, t_idx, ac_idx, aircraft, with_error = False):
    tower_centre = towers.centres[t_idx]
    if with_error:
        aircraft_positions = aircraft.position_error[ac_idx]
    else:
        aircraft_positions = aircraft.positions[ac_idx]

    active_bat = aircraft.flight_times[ac_idx]/aircraft.max_flight_times[ac_idx]

    dist_to_tower = np.linalg.norm(aircraft_positions-tower_centre,axis=1)
    centroid = np.mean(aircraft_positions,axis=0)
    dist_to_centroid = np.linalg.norm(aircraft_positions-centroid,axis=1)

    g = 10
    a = 5

    return np.log(
        1
        + (
            (dist_to_tower + dist_to_centroid)
            / (g * (active_bat + 1e-100) * 100)
        )
    ) ** (active_bat * a)

def get_gateway_leaders(aircraft, towers, active_aircraft, previous_gateways, new_leader = False):
    leaders = []
    heuristic_logs = []
    

    if not new_leader:
        for i,leader in enumerate(previous_gateways):
            if leader is not None and leader in active_aircraft and leader in towers.aircraft_list[i]:
                leaders.append(leader)
            else:
                leaders.append(None)
        
        return leaders,[]
    
    for k, active in enumerate(towers.active):
        if not active: 
            leaders.append(None)
            continue
        
        tower_ac = towers.aircraft_list[k]
        
        if tower_ac == []:
            leaders.append(None)
            continue
        
        if len(tower_ac) <2  and tower_ac[0] in active_aircraft:
            leaders.append(tower_ac[0])
        else:
            candidates = np.intersect1d(tower_ac, active_aircraft)
            if len(candidates) == 0:
                leaders.append(None)
                continue
            heuristics = get_heuristics(towers, k, candidates, aircraft, with_error=True)
            m = np.mean(heuristics)
            true_heuristics = get_heuristics(towers, k, candidates, aircraft, with_error= False)
            best = np.argmin(heuristics)
            true_best = np.argmin(true_heuristics)
            
            if previous_gateways[k] in candidates:
                leaders.append(previous_gateways[k])
            else:
                leaders.append(candidates[best])
            heuristic_logs.append([best, true_best, heuristics, true_heuristics])

    
    return leaders, heuristic_logs



        