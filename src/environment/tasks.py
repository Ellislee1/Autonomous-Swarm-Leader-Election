import numpy as np

class TaskManager:
    def __init__(self, area, towers, n_tasks = 5):
        self.area = area
        self.tasks = np.round(np.random.uniform((0,0), area,(n_tasks,2)),0)
        self.compleated = [0]*n_tasks
        self.check_in_tower(towers)
        
    
    def check_in_tower(self, towers):
        task, tower = towers.get_tower(self.tasks)
        active_status = towers.active[tower]

        while not all(active_status):
            invalid = np.where(active_status == False)[0]
            
            self.tasks[invalid] = np.random.uniform((0,0), self.area,(len(invalid),2))
            
            task, tower = towers.get_tower(self.tasks)
            active_status = towers.active[tower]
        
        self.tower_assignments = tower
    
    def update(self, update_counter, towers):
        pass