import pygame
from src.tower import Tower, ring_to
from src.drone import Drone
from typing import List

from src.leader_selections import *
from src.functions import gen_gradients

from shapely.geometry import Point

FramePerSec = pygame.time.Clock()

RAD = 10

class Environment:
    def __init__(self, screen_size: (int,int) = (800,800), fps:int=60, hex_size:float = 75, n_rings:int = 2, tower_centre:(float,float) = None, n_drones:int = 5, max_signal: List[int] = None, sites = 3):
        if max_signal is None:
            max_signal = [5]
        self.scree_size = self.width,self.height = screen_size
        self.fps = fps

        self.hex_size = hex_size
        self.tower_centre = (self.width/2, self.height/2) if tower_centre is None else tower_centre
        self.gen_tower_env(hex_size, n_rings, max_signal)
        
        self.init_sites(sites)

        self.init_drones(n_drones)

        self.leader = np.random.choice(self.drones)

        pygame.init()
        pygame.display.set_caption(f"Leader elevation with {len(self.drones)} Drones and {n_rings} rings of towers")

        self.screen = pygame.display.set_mode(self.scree_size)
        self.running = False
        
        self.font = pygame.font.SysFont(None, 24)
        
        self.drone_colours = gen_gradients('#3d3d3d','#3b74f7', 10)
        
        print(self.drone_colours)
        
    def gen_tower_env(self, hex_size, n_rings, max_signal):
        self.towers = ring_to(self.tower_centre, n_rings, hex_size, max_signal)
        
    def init_drones(self,n_drones:int):
        self.drones = [Drone(self.scree_size) for _ in range(n_drones)]
        
    def init_sites(self, sites):
        self.sites = []
        for _ in range(sites):
            valid = False
            while not valid:
                site = np.random.uniform((0,0),self.scree_size, 2)

                for tower in self.towers:
                    if not tower.has_hub and tower.includes(Point(site)):
                        self.sites.append(site)
                        tower.has_hub = True
                        valid = True

                        break
        
    def run(self):
        self.running = True
        
        i = 0
        
        # Main loop
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
        
            # Update the env
            self.step(i)
        
            i = (i+1) % self.fps
        
            # Draw elements
            self.draw()
            pygame.display.update()
            FramePerSec.tick(self.fps)
    
    def step(self, i: int):
        self.update_drones()
        self.update_towers(i)
        self.update_leader()
        
    def update_drones(self):
        for drone in self.drones:
            drone.update(1/self.fps, self.scree_size)
            
    def update_towers(self, t):
        self.update_tower_assignments()
        
        if t ==0:
            for tower in self.towers:
                tower.update_bandwith()
            
    def update_tower_assignments(self):
        for drone in self.drones:
            if drone.active_tower is not None:
                if drone.active_tower.includes(drone.point):
                    continue
                drone.active_tower.drop(drone)
                drone.active_tower = None
            
            for tower in self.towers:
                if tower.includes(drone.point):
                    tower.add(drone)
                    drone.active_tower = tower
                    
                    break
    
    def update_leader(self):
        self.leader = strong_signal(self.towers, self.drones, self.leader)
    
    def draw(self):
        self.screen.fill((255,255,255))
        self.draw_towers()
        self.draw_sites()
        self.draw_drones()
        
    def draw_sites(self):
        for site in self.sites:
            site_image = pygame.image.load('assets/launchsite.png')
            site_image = pygame.transform.scale(site_image, (30,30))
            
            self.screen.blit(site_image, site)
        
    def draw_towers(self):
        for tower in self.towers:
            pygame.draw.polygon(self.screen, tower.colour, tower.coords)
            pygame.draw.polygon(self.screen, (50,50,50), tower.coords, width=3)
            img = self.font.render(f'{round(tower.bandwith_as_percent,2)}', True, (0,0,0))
            self.screen.blit(img, tower.centre)
            
    def draw_drones(self):
        for drone in self.drones:
            if drone == self.leader:
                c = (72, 224, 102)
                # pygame.draw.circle(self.screen, (0,0,0), drone.pos, 8)
                pygame.draw.polygon(self.screen, (0,0,0), drone.poly(RAD+4))
            elif drone.is_active:
                c = self.drone_colours[int(((drone.bat*100)//10))]
            else:
                pygame.draw.polygon(self.screen, (self.drone_colours[0]), drone.poly(RAD-2))
                continue
            
            # pygame.draw.circle(self.screen, c, drone.pos, 6)
            pygame.draw.polygon(self.screen, c, drone.poly(RAD))
        