import pygame
import numpy as np

from .text_tools import blit_text

FramePerSec = pygame.time.Clock()

class UI:
    def __init__(self, env:object, screen_size:(int,int), fps:int = 60):
        self.screen_size = self.width,self.height = screen_size
        self.fps = fps
        self.env = env
        
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
        
        
        # Print the current sim time to the screen
        pygame.display.set_caption(f'Sim Time: {self.env.sim_time}')
        self.screen.blit(blit_text(self.screen, (0,0,0), f'Sim Time: {self.env.sim_time}', self.default_font),(3,self.height-21))
        
    def draw_aircraft(self):
        for ac in self.env.state:
            points = []
            rad = self.ac_r if ac[-1] else self.ac_r/2
            
            for i in range(0,360,360//3):
                theta = np.deg2rad((i+ac[4])%360)
        
                points.append([ac[0]+(rad*np.cos(theta)), ac[1]+(rad*np.sin(theta))])
            
            if ac[-1]:
                mid = [(points[1][0]+points[2][0])/2,(points[1][1]+points[2][1])/2]
            
                points.insert(2, [(mid[0]+points[0][0])/2,(mid[1]+points[0][1])/2])
            
            pygame.draw.polygon(self.screen, (0,0,0), points)
    
    def draw_towers(self):
        for tower in self.env.towers:
            if not tower.active:
                continue
            pygame.draw.polygon(self.screen, tower.colour, tower.coords)
            pygame.draw.polygon(self.screen, (50,50,50), tower.coords, width=3)
            img = self.default_font.render(f'{round(tower.bandwith_as_percent,2)}', True, (0,0,0))
            self.screen.blit(img, tower.centre)