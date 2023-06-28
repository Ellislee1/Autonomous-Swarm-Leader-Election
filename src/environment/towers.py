import numpy as np
from typing import List
import itertools
from src.functions import gen_gradients

global DIRECTION_VECTORS, C1, C2
DIRECTION_VECTORS = None
C2='#ddfaac' # Colour 2
C1 = "#FF0000" # Colour 1

class Towers:
    def __init__(self, sizes = 175):
        self.cube_coords = []
        self.offsets = []
        self.max_bandwidths = []
        self.base_bandwidths = []
        self.active = []
        self.sizes = sizes
        self.centres = []
        self.aircraft_list = []
        self.n_towers = 0
        
        self.gradients = gen_gradients(C1, C2, 10)
        
    def update_towers(self, aircraft):
        new_aircraft_list = [[]]*len(self.centres)
        relative_qs = ((2./3)* (aircraft.positions[:,0]-self.offsets[0][0]))/self.sizes
        relative_rs = (((-1./3)*(aircraft.positions[:,0]-self.offsets[0][0]))+((np.sqrt(3)/3)*(aircraft.positions[:,1]-self.offsets[0][1])))/self.sizes
        relative_ss = -relative_qs-relative_rs
        
        coords = axial_round(relative_qs,relative_rs,relative_ss)
        
        tower_assignments = np.where(np.all(coords[:, np.newaxis, :] == self.cube_coords, axis=2))[1]
        
        unique_towers = np.unique(tower_assignments)
        
        # Assign drones to unique towers
        for t in unique_towers:
            new_aircraft_list[t] = np.where(tower_assignments == t)[0]
        
        self.aircraft_list = new_aircraft_list
        
    @property
    def active_idxs(self):
        return np.where(self.active)
    
    def get_gradient(self,i):
        colour_idx = max(int(self.bandwith_as_percent(i)*len(self.gradients))-1,0)
        return self.gradients[colour_idx]
        
    
    def gen_rings(self, centre:(float, float), rings:int, max_bandwidth:List[int]):
        # Add the centre tower:
        self.add_towers([[0, 0, centre, np.random.choice(max_bandwidth), 0, True, get_vertices(centre, self.sizes), centre]])
        
        for k in range(1, rings):
            self.gen_ring(k,max_bandwidth)
        
    def gen_ring(self, k, max_bandwidth):
        _max_bandwidth = np.random.choice(max_bandwidth)
        _hex = create_hex(self[0], scale(direction_hex(4),k,self.sizes,self.offsets[0],_max_bandwidth,0,True), self.sizes, self.offsets[0], _max_bandwidth, 0, True)
        for i, _ in itertools.product(range(6), range(k)):
            self.add_towers([_hex])
            _hex = neighbor(_hex, i, self.sizes, self.offsets[0], np.random.choice(max_bandwidth))

            
    def __getitem__(self, i):
        return [*self.cube_coords[i], self.offsets[i], self.max_bandwidths[i], self.base_bandwidths[i], self.active[i], self.shape_verts[i], self.centres[i]]
    
    def bandwith_as_percent(self,i):
        return max(1-((self.base_bandwidths[i]+len(self.aircraft_list[i]))/self.max_bandwidths[i]),0)
    
    def get_centre(self, i):
        return self.centres[i]
    
    def add_towers(self, towers):
        for tower in towers:
            if self.n_towers == 0:
                self.form_new_set(tower)
            else:
                self.append_tower(tower)

            self.n_towers += 1

    def form_new_set(self, tower):
        self.cube_coords = np.array([tower[:2]])
        self.offsets = np.array([tower[2]])
        self.max_bandwidths = np.array([tower[3]])
        self.base_bandwidths = np.array([tower[4]])
        self.active = np.array([tower[5]])
        self.shape_verts = np.array([tower[6]])
        self.centres = np.array([tower[7]])
        self.aircraft_list.append([])

    def append_tower(self, tower):
        self.cube_coords = np.append(self.cube_coords, [tower[:2]], axis=0)
        self.offsets = np.append(self.offsets, [tower[2]], axis=0)
        self.max_bandwidths = np.append(self.max_bandwidths,[tower[3]], axis=0)
        self.base_bandwidths = np.append(self.base_bandwidths, [tower[4]], axis=0)
        self.active = np.append(self.active, [tower[5]], axis=0)
        self.shape_verts = np.append(self.shape_verts,[tower[6]], axis=0)
        self.centres = np.append(self.centres,[tower[7]], axis=0)
        self.aircraft_list.append([])
        
    def xy_to_cubic_hex(self, points):
        relative_qs = ((2./3)* (points[:,0]-self.offsets[0]))/self.sizes
        relative_rs = (((-1./3)*(points[:,0]-self.offsets[0]))+((np.sqrt(3)/3)*(points[:,1]-self.offsets[1])))/self.sizes
        relative_ss = -relative_qs-relative_rs
        
        return axial_round(relative_qs, relative_rs, relative_ss)
    

def axial_round(relative_qs, relative_rs, relative_ss):
    q = np.round(relative_qs).astype(int)
    r = np.round(relative_rs).astype(int)
    s = np.round(relative_ss).astype(int)
    
    q_diff,r_diff,s_diff = np.abs(q-relative_qs),np.abs(r-relative_rs), np.abs(s-relative_ss)
    
    q_idxs = np.where(np.logical_and(q_diff > r_diff, q_diff > s_diff))[0]
    r_idxs = np.setdiff1d(np.where(r_diff > s_diff)[0], q_idxs)
    s_idxs = np.setdiff1d(np.array(list(range(len(q)))), np.union1d(q_idxs, r_idxs))
    
    q[q_idxs] = -r[q_idxs]-s[q_idxs]
    r[r_idxs] = -q[r_idxs]-s[r_idxs]
    # s[s_idxs] = -q[s_idxs]-r[s_idxs]
        
    return np.array(list(zip(q,r)))
  
def get_vertices(centre, size):
    return np.asarray([
        [
            centre[0] + (size * np.cos((np.pi/3) * (i+1))),
            centre[1] + (size * (np.sin((np.pi/3) * (i+1))))
        ] for i in range(6)
    ])
    
def cubic_hex_to_xy(points, offsets, size):
    x = offsets[:,0] + (size * ((3./2)*points[:,0]))
    y = offsets[:,1] + (size *(((np.sqrt(3)/2)*points[:,0]) + (np.sqrt(3)*points[:,1])))
    return np.array(list(zip(x,y)))

def direction_hex(direction):
    global DIRECTION_VECTORS
    if DIRECTION_VECTORS is None:
        DIRECTION_VECTORS = [
            [+1,0],
            [+1,-1],
            [0,-1],
            [-1,0],
            [-1,+1],
            [0,+1]
        ]
    
    return DIRECTION_VECTORS[direction]

def neighbor(_hex, direction, size, offset, max_bandwidth):
    return create_hex(_hex, direction_hex(direction), size, offset, max_bandwidth, 0, True)

def scale(_hex, factor, size, offset, max_bandwidth, base_bandwidth, active):
    coordinates = np.array(_hex[:2])*factor
    xy_coordinates = cubic_hex_to_xy(np.array([coordinates]), np.array([offset]), size)[0]
    return [*coordinates, offset, max_bandwidth, base_bandwidth, active, get_vertices(xy_coordinates, size)]

def create_hex(_hex, _vec, size, offset, max_bandwidth, base_bandwidth, active):
    coordinates = [_hex[0]+_vec[0], _hex[1]+_vec[1]]
    xy_coordinates = cubic_hex_to_xy(np.array([coordinates]), np.array([offset]), size)[0]
    
    return [*coordinates, offset, max_bandwidth, base_bandwidth, active, get_vertices(xy_coordinates, size),xy_coordinates]