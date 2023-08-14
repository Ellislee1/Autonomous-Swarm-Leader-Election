import numpy as np

class TaskManager:
    def __init__(self, area, towers, n_tasks = 5):
        self.area = area
        self.tasks = np.round(np.random.uniform((0,0), area,(n_tasks,2)),0)
        self.check_in_tower(towers)
        self.compleated = np.zeros(len(self.tasks))
        
    
    def check_in_tower(self, towers):
        task, tower = towers.get_tower(self.tasks)
        active_status = towers.active[tower]

        while not all(active_status):
            invalid = np.where(active_status == False)[0]
            
            self.tasks[invalid] = np.random.uniform((0,0), self.area,(len(invalid),2))
            
            task, tower = towers.get_tower(self.tasks)
            active_status = towers.active[tower]
        
        self.tower_assignments = tower
    
    def update(self, update_counter, towers, aircraft, ts):


        for i in range(len(self.tower_assignments)):
            dupes = len(np.where(self.tower_assignments == self.tower_assignments[i])[0])
            reg_ac = towers.aircraft_list[self.tower_assignments[i]]
            ac_active_status = aircraft.aircraft.active[reg_ac]
            
            self.compleated[i] += np.round((len(np.where(ac_active_status)[0])*ts)/dupes,3)

        print(self.compleated)
        
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

        self.tasks = np.array(new_tasks)
        self.compleated = np.array(new_compleated)
        self.check_in_tower(towers)