import numpy as np

def update_waypoints(ac_positions, waypoints, active_2IC, world_bounds, towers, active_ac, tasks):
    dist = np.linalg.norm(ac_positions-waypoints, axis=-1)

    update = np.where(dist <= 15)[0]

    new_waypoints = np.copy(waypoints)

    active_2IC = np.copy(active_2IC)
    active_2IC[active_2IC == None] = -1
    # update generic
    idxs = np.setdiff1d(update, active_2IC) if active_2IC is not None else update
    new_waypoints[idxs] = np.random.randint((0,0),world_bounds, (len(idxs),2))

    new_waypoints = update_task_waypoints(ac_positions, new_waypoints, active_2IC, towers, active_ac, tasks, update)
    
    for idx in active_2IC:
        if idx == -1:
            continue

        tower = np.where(active_2IC == idx)[0][0]
        centre = towers.centres[tower]

        assigned = towers.aircraft_list[tower]
        valid = np.intersect1d(assigned,active_ac)


        if (idx in update and len(valid)>1) or (len(valid)>1 and np.linalg.norm(waypoints[idx]-centre) >= towers.sizes):
            new_waypoints[idx] = np.random.normal(centre,50,2)
        elif idx in update:
            new_waypoints[idx] = np.random.randint((0,0),world_bounds, 2)

    new_waypoints = np.clip(new_waypoints, [0,0], world_bounds)
    return new_waypoints

def update_task_waypoints(ac_positions, waypoints, active_2IC, towers, active_ac, tasks, update):
    assignments = towers.get_tower(tasks)
    unique = np.unique(assignments[-1])
    
    for tower in unique:
        active_tower_ac = np.intersect1d(towers.aircraft_list[tower],active_ac)
        
        if len(active_tower_ac) <= 0:
            continue
        
        normal_update = np.intersect1d(active_tower_ac, update)
        
        wpt_dists = np.linalg.norm(waypoints[active_tower_ac]-towers.centres[tower], axis=1)
        dist_update = active_tower_ac[np.where(wpt_dists >= 200)[0]]
        
        to_update = np.concatenate((dist_update,normal_update))
                
        # tasks = np.where(assignments[-1] == tower)[0]
        waypoints[to_update] = np.random.normal(towers.centres[tower],70,(len(to_update),2))
        
    
    return waypoints