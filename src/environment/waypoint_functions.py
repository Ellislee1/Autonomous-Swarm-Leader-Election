import numpy as np

def update_waypoints(ac_positions, waypoints, active_2IC, world_bounds, towers, active_ac):
    dist = np.linalg.norm(ac_positions-waypoints, axis=-1)

    update = np.where(dist <= 15)[0]

    new_waypoints = np.copy(waypoints)

    active_2IC = np.copy(active_2IC)
    active_2IC[active_2IC == None] = -1
    # update generic
    idxs = np.setdiff1d(update, active_2IC) if active_2IC is not None else update
    new_waypoints[idxs] = np.random.randint((0,0),world_bounds, (len(idxs),2))


    for idx in active_2IC:
        if idx == -1:
            continue
        
        tower = np.where(active_2IC == idx)[0][0]
        centre = towers.centres[tower]
        
        assigned = towers.aircraft_list[tower]
        valid = np.intersect1d(assigned,active_ac)
        
        
        if (idx in update and len(valid)>1) or (len(valid)>1 and np.linalg.norm(waypoints[idx]-centre) >= towers.sizes):
            new_waypoints[idx] = np.random.normal(centre,50,2)
        elif idx in update and len(valid)<=1:
            new_waypoints[idx] = np.random.randint((0,0),world_bounds, 2)
            

    return new_waypoints