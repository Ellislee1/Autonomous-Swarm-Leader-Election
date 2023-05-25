from src.drone import Drone
import numpy as np

def max_bat(drones, leader = None):
    
    for drone in drones:
        if not drone.is_active:
            continue
        
        if (leader is not None and drone.bat > leader.bat) or leader is None:
            leader = drone
    
    return leader


def strong_signal(towers, drones, leader = None):
    if leader is None or leader.active_tower is None:
        max_bandwith = -1
    else:
        max_bandwith = leader.active_tower.bandwith_as_percent

    for tower in towers:
        if (
            tower.bandwith_as_percent > 0
            and tower.bandwith_as_percent > max_bandwith
        ):
            leader = max_bat(tower.drones)
            max_bandwith = tower.bandwith_as_percent
        elif len(tower.drones) == max_bandwith:
            leader = max_bat(tower.drones, leader)

    if leader is None or not leader.is_active:
        leader = max_bat(drones)

    return leader