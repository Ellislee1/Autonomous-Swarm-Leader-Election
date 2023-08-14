import numpy as np

class TaskManager:
    def __init__(self, area, n_tasks = 5):
        self.area = area
        self.tasks = np.random.uniform((0,0), area,(n_tasks,2))
        print(self.tasks)
        
        
    def update(self, update_counter):
        pass