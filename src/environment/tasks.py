import numpy as np

class TaskManager:
    def __init__(self, area, towers, n_tasks = 0, random_tasks = True, n_random = 7, rand_interval = (30,30)):
        self.area = area
        tasks = np.round(np.random.uniform((0,0), area,(n_tasks,2)),0)
        self.tasks, self.tower_assignments = self.check_in_tower(tasks, towers)
        self.compleated = np.zeros(len(self.tasks))
        self.total_tasks = len(self.tasks)
        self.random_tasks = random_tasks
        self.n_random = n_random
        self.rand_interval = rand_interval
        
        self.next_random = np.random.choice(self.rand_interval)
        self.log = []
    
    def save_log(self, path):
        np.save(path, self.log)
    
    def add_tasks(self, towers, n_tasks = 1):
        tasks = np.round(np.random.uniform((0,0), self.area,(n_tasks,2)),0)
        
        tasks, tower_assignments = self.check_in_tower(tasks, towers)
        
        if len(self.tasks)>0:
            self.tasks = np.append(self.tasks, tasks, axis=0)
            self.compleated = np.append(self.compleated, [0]*n_tasks,axis=0)
            self.tower_assignments = np.append(self.tower_assignments, tower_assignments,axis=0)
        else:
            self.tasks = tasks
            self.compleated = np.array([0])
            self.tower_assignments = tower_assignments
        
        self.total_tasks += n_tasks
    
    def check_in_tower(self, tasks, towers):
        task, tower = towers.get_tower(tasks)
        active_status = towers.active[tower]

        while not all(active_status):
            invalid = np.where(active_status == False)[0]
            
            tasks[invalid] = np.round(np.random.uniform((0,0), self.area,(len(invalid),2)),0)
            
            task, tower = towers.get_tower(tasks)
            active_status = towers.active[tower]
        
        return tasks,tower
    
    def update(self, update_counter, towers, aircraft, sim_time,ts, active_gateways):
        if sim_time>= self.next_random:
            self.add_tasks(towers,n_tasks=self.n_random)
            self.next_random += np.random.choice(self.rand_interval)

        if len(self.compleated)<len(self.tasks):
            d = len(self.tasks)-len(self.compleated)
            self.compleated = np.append(self.compleated, np.zeros(d))

        cycle = []
        for i in range(len(self.tower_assignments)):
            tower_idx = self.tower_assignments[i]
            dupes = len(np.where(self.tower_assignments == self.tower_assignments[i])[0])
            reg_ac = towers.aircraft_list[self.tower_assignments[i]]
            ac_active_status = aircraft.aircraft.active[reg_ac]
            active_idxs = np.where(ac_active_status)[0]
            active_ac = np.array(reg_ac)[active_idxs]
            gateway = active_gateways[tower_idx]
            if gateway:
                active_ac = active_ac[active_ac != gateway]

            update_val = np.round((len(active_idxs)*ts)/dupes,3)*1.5
            self.compleated[i] += update_val

            cycle.append([i, len(active_idxs), update_val, self.compleated])

            if len(active_ac)> 0:
                if gateway:
                    centre = aircraft.aircraft.position_error[gateway]

                else:
                    centre = towers.centres[self.tower_assignments[i]]
        self.log.append([cycle, self.total_tasks, len(self.tasks)])


        finished = np.where(self.compleated >=100.)[0]
        if len(finished) > 0:
            self.update_tasks(finished, towers)

    def update_tasks(self, finished, towers):
        new_tasks = []
        new_compleated = []

        for i in range(len(self.tasks)):
            if i not in finished:
                new_tasks.append(self.tasks[i])
                new_compleated.append(self.compleated[i])

        tasks = np.array(new_tasks)
        self.compleated = np.array(new_compleated)
        self.tasks,self.tower_assignments = self.check_in_tower(tasks, towers)