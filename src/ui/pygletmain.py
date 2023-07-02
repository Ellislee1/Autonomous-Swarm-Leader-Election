import pyglet
import numpy as np
import time
from datetime import datetime, timedelta

class InfoUI(pyglet.window.Window):
    def __init__(self,screen_size:(int,int), env):
        super().__init__(*screen_size, resizable=True)
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
        
        batch.draw()
        

class SimUI(pyglet.window.Window):
    def __init__(self, env:object, screen_size:(int,int), fps:int = 60):
        super().__init__(*screen_size)
        self.env = env
        self.colours = [(0,0,0,255), (128,128,128,255),(96, 139, 209,255),(2, 64, 247,255),(0,200,0,255)]
        self.ac_r = 10
        # self.tower_batch = pyglet.graphics.Batch()
        
        # pyglet.clock.schedule_interval(self.update, 1/60)
    
    def update(self, fps):
       pass
    
    def on_draw(self):
        self.clear()
        self.draw_towers()
        self.draw_aircraft()
    
    def draw_towers(self):
        tower_batch = pyglet.graphics.Batch()
        elem_list = []
        for idx in self.env.towers.active_idxs[0]:
            c = self.env.towers.get_gradient(idx).replace('#','')
            hexagon = pyglet.shapes.Polygon(*self.env.towers[idx][6].tolist(),
            color=tuple(int(c[i:i+2], 16) for i in (0, 2, 4)), batch=tower_batch)
            
            label = pyglet.text.Label(f'Tower {idx}', color = (0,0,0,255),font_size=12, x=self.env.towers[idx][7][0], y=self.env.towers[idx][7][1]+9, anchor_x='center', anchor_y='center', batch=tower_batch)
            label2 = pyglet.text.Label(f'Bandwidth: {round(self.env.towers.bandwith_as_percent(idx),2)}', color = (0,0,0,255),font_size=12, x=self.env.towers[idx][7][0], y=self.env.towers[idx][7][1]-9, anchor_x='center', anchor_y='center', batch=tower_batch)
            
            elem_list.append((hexagon,label,label2))
            
            # hexagon.draw()
            # label.draw()
            # label2.draw()
        
        tower_batch.draw()
            
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
                colour = (255, 255, 255,200)
            else:
                outline_rad = rad + 3
                colour = (0,0,0,100)
                
            colour_idx = min(int((len(self.colours)-1)*(1-ac[7]/ac[8]))+1, len(self.colours)-1) if ac[7] <= ac[8] else 0
            
            for i in range(0,360,360//3):
                theta = np.deg2rad((i+ac[4])%360)

                points.append([ac[0]+(rad*np.cos(theta)), ac[1]+(rad*np.sin(theta))])
                outline.append([ac[0]+(outline_rad*np.cos(theta)), ac[1]+(outline_rad*np.sin(theta))])
            label = None
            if ac[-1]:
                mid = [(points[1][0]+points[2][0])/2,(points[1][1]+points[2][1])/2]
                outline_mid = [(outline[1][0]+outline[2][0])/2,(outline[1][1]+outline[2][1])/2]

                points.insert(2, [(mid[0]+points[0][0])/2,(mid[1]+points[0][1])/2])
                outline.insert(2, [(outline_mid[0]+outline[0][0])/2,(outline_mid[1]+outline[0][1])/2])

                # pygame.draw.polygon(self.screen, colour, outline)
                outline = pyglet.shapes.Polygon(*outline,color=colour, batch=ac_batch)
                label = pyglet.text.Label(f'{k}', color = (255,255,255,255),font_size=12, bold=True, x=ac[0]-(rad), y=ac[1]-(rad), anchor_x='center', anchor_y='center', batch=ac_batch)
                # label = pyglet.text.Label(f'{k}', color = (0,0,0,255),font_size=12, bold=True, x=ac[0]-(rad), y=ac[1]-(rad), anchor_x='center', anchor_y='center', batch=ac_batch)
                # poly.draw()
                
                # img = self.default_font.render(f'{k}', True, (0,0,0))
                # self.screen.blit(img, ac[:2])

                # with contextlib.suppress(Exception):
                #     pygame.draw.lines(self.screen, (255, 0, 255), False, last_n[:,k,:2], width=2)
            # pygame.draw.polygon(self.screen, self.colours[colour_idx], points)
            ac = pyglet.shapes.Polygon(*points,color=self.colours[colour_idx], batch=ac_batch)
            
            ac_elems.append((outline,ac, label))
            
        ac_batch.draw()
            
            

