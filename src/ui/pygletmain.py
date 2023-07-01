import pyglet
import numpy as np

class SimUI(pyglet.window.Window):
    def __init__(self, env:object, screen_size:(int,int), fps:int = 60):
        super().__init__(*screen_size)
        self.env = env
    
    def on_draw(self):
        self.clear()
        self.draw_towers()
    
    def draw_towers(self):
        for idx in self.env.towers.active_idxs[0]:
            # print(self.env.towers[idx][6].tolist())
            c = self.env.towers.get_gradient(idx).replace('#','')
            # print(*self.env.towers[idx][6].tolist())
            hexagon = pyglet.shapes.Polygon(*self.env.towers[idx][6].tolist(),
            color=tuple(int(c[i:i+2], 16) for i in (0, 2, 4)))
            hexagon.draw()
            label = pyglet.text.Label(f'Tower {idx}', color = (0,0,0,255),font_size=12, x=self.env.towers[idx][7][0], y=self.env.towers[idx][7][1]+9, anchor_x='center', anchor_y='center')
            label.draw()
            label = pyglet.text.Label(f'Bandwidth: {round(self.env.towers.bandwith_as_percent(idx),2)}', color = (0,0,0,255),font_size=12, x=self.env.towers[idx][7][0], y=self.env.towers[idx][7][1]-9, anchor_x='center', anchor_y='center')
            label.draw()
            # break
             
            # pygame.draw.polygon(self.screen, self.env.towers.get_gradient(idx), self.env.towers[idx][6])
            # pygame.draw.polygon(self.screen, (50,50,50), self.env.towers[idx][6], width=3)
            # img = self.default_font.render(f'{idx},{round(self.env.towers.bandwith_as_percent(idx),2)}', True, (0,0,0))
            # self.screen.blit(img, self.env.towers.get_centre(idx))