from src.drone import Drone
import numpy as np

def max_bat(drones, leader = None):
    for drone in drones:
        if not drone.is_active:
            continue

        if leader is None or drone.bat > leader.bat:
            leader = drone
    
    return leader


def strong_signal(towers, drones, leader = None):
    if leader is None or leader.active_tower is None or not leader.active_tower.active:
        max_bandwith = -1
        leader = None
    else:
        max_bandwith = leader.active_tower.bandwith_as_percent

    for tower in towers:
        if not tower.active:
            continue
        if (tower.bandwith_as_percent > max_bandwith and tower.n_drones > 0
        ):
            leader = max_bat(tower.drones)
            max_bandwith = tower.bandwith_as_percent
        elif tower.bandwith_as_percent == max_bandwith and tower.n_drones > 0:
            leader = max_bat(tower.drones, leader)

    if leader is None or not leader.is_active:
        leader = None

    return leader