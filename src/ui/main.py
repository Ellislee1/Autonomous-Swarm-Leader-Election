import contextlib
import pygame
import numpy as np
import time
from datetime import datetime, timedelta

from .text_tools import blit_text

FramePerSec = pygame.time.Clock()

class UI:
    def __init__(self, env:object, screen_size:(int,int), fps:int = 60):
        self.screen_size = self.width,self.height = screen_size
        self.fps = fps
        self.env = env
        self.colours = [(0,0,0), (128,128,128),(96, 139, 209),(2, 64, 247),(0,200,0)]
        
        self.ac_r = 10
        
        self.post_init()
        
    def post_init(self):
        pygame.init()
        pygame.display.set_caption('Temp')
        
        self.screen = pygame.display.set_mode(self.screen_size)
        self.running = False
        
        self.default_font = pygame.font.SysFont('monospace', 18)
        
    def run(self):
        self.running = True
        
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            if not self.env.running:
                self.running = False
            
            self.draw_screen()
            FramePerSec.tick(self.fps)
    
    def draw_screen(self):
        self.screen.fill((255,255,255))
        
        self.draw_towers()
        self.draw_aircraft()
        
        
        # Print the current sim time. This should be last
        self.draw_sim_info()
        pygame.display.update()
        
    def draw_sim_info(self):
        pygame.draw.rect(self.screen, (170,170,170), pygame.Rect(0, self.height-30, self.width, self.height-24))
        time_passed = (time.perf_counter() - self.env.start_time) * 1000
        wall_time = (datetime(1,1,1)+timedelta(milliseconds=time_passed)).strftime("%H:%M:%S.%f")[:-4]
        info_text = f'Sim Time: {self.env.sim_time} (Wall Time: {wall_time})\tActive Aircraft: {self.env.active_ac}/{len(self.env.state.positions)}'
        
        # Print the current sim time to the screen
        pygame.display.set_caption(info_text)
        self.screen.blit(blit_text(self.screen, (0,0,0), info_text, self.default_font),(3,self.height-21))
        
    def draw_aircraft(self):
        # last_n = np.array(self.env.log[-(int((1/self.env.ts)/self.env.scale)):])
        last_n = 100
        for k, ac in enumerate(self.env.state):
            points = []
            outline = []
            rad = self.ac_r if ac[-1] else self.ac_r/2
            
            if self.env.leader_election.are_leaders is not None and k in self.env.leader_election.are_leaders:
                outline_rad = rad + 5
                colour = (255,0,0)
            elif k in self.env.leader_election.are_2IC:
                outline_rad = rad + 5
                colour = (255, 255, 255)
            else:
            
                outline_rad = rad + 3
                colour = (0,0,0)

            colour_idx = min(int((len(self.colours)-1)*(1-ac[7]/ac[8]))+1, len(self.colours)-1) if ac[7] <= ac[8] else 0

            for i in range(0,360,360//3):
                theta = np.deg2rad((i+ac[4])%360)

                points.append([ac[0]+(rad*np.cos(theta)), ac[1]+(rad*np.sin(theta))])
                outline.append([ac[0]+(outline_rad*np.cos(theta)), ac[1]+(outline_rad*np.sin(theta))])

            if ac[-1]:
                mid = [(points[1][0]+points[2][0])/2,(points[1][1]+points[2][1])/2]
                outline_mid = [(outline[1][0]+outline[2][0])/2,(outline[1][1]+outline[2][1])/2]

                points.insert(2, [(mid[0]+points[0][0])/2,(mid[1]+points[0][1])/2])
                outline.insert(2, [(outline_mid[0]+outline[0][0])/2,(outline_mid[1]+outline[0][1])/2])

                pygame.draw.polygon(self.screen, colour, outline)
                
                img = self.default_font.render(f'{k}', True, (0,0,0))
                self.screen.blit(img, ac[:2])

                with contextlib.suppress(Exception):
                    pygame.draw.lines(self.screen, (255, 0, 255), False, last_n[:,k,:2], width=2)
            pygame.draw.polygon(self.screen, self.colours[colour_idx], points)
    
    def draw_towers(self):
        
        for idx in self.env.towers.active_idxs[0]:
            pygame.draw.polygon(self.screen, self.env.towers.get_gradient(idx), self.env.towers[idx][6])
            pygame.draw.polygon(self.screen, (50,50,50), self.env.towers[idx][6], width=3)
            img = self.default_font.render(f'{idx},{round(self.env.towers.bandwith_as_percent(idx),2)}', True, (0,0,0))
            self.screen.blit(img, self.env.towers.get_centre(idx))