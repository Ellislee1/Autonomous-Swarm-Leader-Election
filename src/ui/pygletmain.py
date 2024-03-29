import pyglet
import numpy as np
import time
from datetime import datetime, timedelta

class InfoUI(pyglet.window.Window):
    def __init__(self,screen_size:(int,int), env):
        super().__init__(*screen_size, resizable=False, )
        self.env = env
        self.screen_size = self.width,self.height = screen_size
        
        
    def on_draw(self):
        self.clear()
        self.draw_env_info()
    
    def draw_env_info(self):
        batch = pyglet.graphics.Batch()
        sim_time = pyglet.text.Label(f'Sim Time: {self.env.sim_time}', color = (255,255,255,255),font_size=14, x=10, y=self.height-14, anchor_x='left', anchor_y='center', batch=batch)

        time_passed = (time.perf_counter() - self.env.start_time) * 1000
        wall_time = (datetime(1,1,1)+timedelta(milliseconds=time_passed)).strftime("%H:%M:%S.%f")[:-4]
        wall_time_label = pyglet.text.Label(f'Wall Time: {wall_time}', color = (255,255,255,255),font_size=14, x=10, y=self.height-(14*2)-5, anchor_x='left', anchor_y='center', batch=batch)

        active_ac = pyglet.text.Label(f'Active Aircraft: {self.env.active_ac}/{len(self.env.state.positions)}', color = (255,255,255,255),font_size=14, x=10, y=self.height-(14*3)-(5*2), anchor_x='left', anchor_y='center', batch=batch)

        active_tasks = pyglet.text.Label(f'Active Tasks: {len(self.env.task_manager.tasks)}/{self.env.task_manager.total_tasks}', color = (255,255,255,255),font_size=14, x=10, y=self.height-(14*4)-(5*3), anchor_x='left', anchor_y='center', batch=batch)
        
        batch_break = pyglet.text.Label(
            '-------- Batch Info --------',
            color=(255, 255, 255, 255),
            font_size=14,
            x=self.width//2,
            y=self.height - (14 * 5) - (5 * 4),
            anchor_x='center',
            anchor_y='center',
            batch=batch,
        )

        sim_batch = pyglet.text.Label(f'Sim Batch: {self.env.sim_run}/{self.env.max_batches}', color = (255,255,255,255),font_size=14, x=10, y=self.height-(14*6)-(5*5), anchor_x='left', anchor_y='center', batch=batch)
        time_passed = (time.perf_counter() - self.env.t_delta) * 1000
        t_wall = (datetime(1,1,1)+timedelta(milliseconds=time_passed)).strftime("%H:%M:%S.%f")[:-4]
        batch_time = pyglet.text.Label(f'Total Wall Time: {t_wall}', color = (255,255,255,255),font_size=14, x=10, y=self.height-(14*7)-(5*6), anchor_x='left', anchor_y='center', batch=batch)
        batch.draw()
        

class SimUI(pyglet.window.Window):
    def __init__(self, env:object, screen_size:(int,int), fps:int = 60):
        super().__init__(*screen_size)
        self.env = env
        self.screen_size = screen_size
        self.colours = [(0,0,0,255), (128,128,128,255),(96, 139, 209,255),(2, 64, 247,255),(0,200,0,255)]
        self.ac_r = 10
        # self.tower_batch = pyglet.graphics.Batch()
        
        # pyglet.clock.schedule_interval(self.update, 1/60)
    
    def update(self, fps):
       pass
    
    def on_draw(self):
        self.clear()
        self.draw_towers()
        self.draw_tasks()
        self.draw_aircraft()
    
    def draw_towers(self):
        tower_batch = pyglet.graphics.Batch()
        elem_list = []
        
        bg = pyglet.shapes.Rectangle(0, 0, *self.screen_size, batch=tower_batch, color=(255,255,255,250))
        
        for idx in self.env.towers.active_idxs[0]:
            c = self.env.towers.get_gradient(idx).replace('#','')
            hexagon = pyglet.shapes.Polygon(*self.env.towers[idx][6].tolist(),
            color=tuple(int(c[i:i+2], 16) for i in (0, 2, 4)), batch=tower_batch)
            
            label = pyglet.text.Label(f'Tower {idx}', color = (0,0,0,255),font_size=12, x=self.env.towers[idx][7][0], y=self.env.towers[idx][7][1]+9, anchor_x='center', anchor_y='center', batch=tower_batch)
            label2 = pyglet.text.Label(f'# Drones: {len(self.env.towers.aircraft_list[idx])}', color = (0,0,0,255),font_size=12, x=self.env.towers[idx][7][0], y=self.env.towers[idx][7][1]-9, anchor_x='center', anchor_y='center', batch=tower_batch)
            
            elem_list.append((hexagon,label,label2))
            
            # hexagon.draw()
            # label.draw()
            # label2.draw()
        
        tower_batch.draw()
        
    
    def draw_tasks(self):
        task_batch = pyglet.graphics.Batch()
        task_elems = []
        
        for i, task in enumerate(self.env.task_manager.tasks):
            try:
                percent = (self.env.task_manager.compleated[i]/100)
                t = pyglet.text.Label('!',font_size=24, anchor_x='center', align='center', batch=task_batch, x=task[0], y=task[1], color=(int(255*(1-percent)),int(255*percent),0,255), bold = True)
                # s = pyglet.shapes.Circle(*task,radius=3,color=(255,0,0,255), batch=task_batch)
                task_elems.append(t)
            except IndexError: # I am not sure what causes this issue yet but it is breaking the system
                print('Index {i} out of bounds skipping ...')
        
        task_batch.draw()
    
    def draw_aircraft(self):
        ac_batch = pyglet.graphics.Batch()
        ac_elems = []
        
        
        for k, ac in enumerate(self.env.state):
            points = []
            outline = []
            rad = self.ac_r if ac[-1] else self.ac_r/2
            
            if self.env.leader_election.are_leaders is not None and k in self.env.leader_election.are_leaders:
                outline_rad = rad + 5
                colour = (255,0,0,255)
            elif k in self.env.leader_election.are_2IC:
                outline_rad = rad + 5
                colour = (0, 255, 0,255)
            else:
                outline_rad = rad + 3
                colour = (0,0,0,100)
            
            for i in range(0,360,360//3):
                theta = np.deg2rad((i+ac[4])%360)

                points.append([ac[0]+(rad*np.cos(theta)), ac[1]+(rad*np.sin(theta))])
                outline.append([ac[0]+(outline_rad*np.cos(theta)), ac[1]+(outline_rad*np.sin(theta))])
            label = None
            error = None
            if ac[-1]:
                error = [[ac[0],ac[1]], ac[9].tolist()]
                mid = [(points[1][0]+points[2][0])/2,(points[1][1]+points[2][1])/2]
                outline_mid = [(outline[1][0]+outline[2][0])/2,(outline[1][1]+outline[2][1])/2]

                points.insert(2, [(mid[0]+points[0][0])/2,(mid[1]+points[0][1])/2])
                outline.insert(2, [(outline_mid[0]+outline[0][0])/2,(outline_mid[1]+outline[0][1])/2])

                # pygame.draw.polygon(self.screen, colour, outline)
                outline = pyglet.shapes.Polygon(*outline,color=colour, batch=ac_batch)
                error = pyglet.shapes.Line(*error[0], *error[1], width=2, color=(255,255,255,255), batch=ac_batch)
                label = pyglet.text.Label(f'{k}', color = (255,255,255,255),font_size=12, bold=True, x=ac[0]-(rad), y=ac[1]-(rad), anchor_x='center', anchor_y='center', batch=ac_batch)
                # label = pyglet.text.Label(f'{k}', color = (0,0,0,255),font_size=12, bold=True, x=ac[0]-(rad), y=ac[1]-(rad), anchor_x='center', anchor_y='center', batch=ac_batch)
                # poly.draw()
                
                # img = self.default_font.render(f'{k}', True, (0,0,0))
                # self.screen.blit(img, ac[:2])

                # with contextlib.suppress(Exception):
                #     pygame.draw.lines(self.screen, (255, 0, 255), False, last_n[:,k,:2], width=2)
            # pygame.draw.polygon(self.screen, self.colours[colour_idx], points)
            
            
            bat_percent = (ac[7])/(ac[8])
            if bat_percent <1:
                
                x = int(104*bat_percent)
                y = int((255-104)*bat_percent)
                ac_ = pyglet.shapes.Polygon(*points,color=(x,x,255-y), batch=ac_batch)
            else:
                ac_ = pyglet.shapes.Polygon(*points,color=(0,0,0), batch=ac_batch)
            
            if ac[-1]:
                waypoint = self.env.state.waypoints[k]
                wpt_line = pyglet.shapes.Line(*waypoint, *self.env.state.positions[k], color=(0,0,0,255), batch=ac_batch)
                wpt = pyglet.shapes.Circle(*waypoint,15,color=(0,0,0,100), batch=ac_batch)
                
            else:
                wpt = None
                wpt_line = None
            ac_elems.append((outline,ac_, label, error, wpt, wpt_line))
            
        ac_batch.draw()
            
            

