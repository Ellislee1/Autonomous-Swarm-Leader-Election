import contextlib
import itertools
from math import sqrt, cos, sin,pi
import numpy as np
from typing import List
from shapely.geometry import Polygon, Point

from src.functions import gen_gradients

# from src.drone import Drone

DIRECTION_VECTORS = {} # Place holder varable 
C2='#ddfaac' # Colour 2
C1 = "#FF0000" # Colour 1

def axial_round(rel_q,rel_r,rel_s):
    """This function performs an axis aligned rounding for faster coordinate indexing when updating towers.
    """
    q = np.round(rel_q).astype(int)
    r = np.round(rel_r).astype(int)
    s = np.round(rel_s).astype(int)
    
    q_diff,r_diff,s_diff = np.abs(q-rel_q),np.abs(r-rel_r), np.abs(s-rel_s)
    
    q_idxs = np.where(np.logical_and(q_diff > r_diff, q_diff > s_diff))[0]
    r_idxs = np.setdiff1d(np.where(r_diff > s_diff)[0], q_idxs)
    s_idxs = np.setdiff1d(np.array(list(range(len(q)))), np.union1d(q_idxs, r_idxs))
    
    q[q_idxs] = -r[q_idxs]-s[q_idxs]
    r[r_idxs] = -q[r_idxs]-s[r_idxs]
    s[s_idxs] = -q[s_idxs]-r[s_idxs]
        
    return np.array(list(zip(q,r,s)))

class Tower_List:
    """This class stores a list of the existing towers
    """
    def __init__(self, towers:None):
        self.tower_list = []
        self.tower_idxs = []
        
        if towers:
            self.add_towers(towers)
    
    def add_towers(self, towers):
        for tower in towers:
            self.tower_list.append(tower)
            self.tower_idxs.append(np.asarray(tower.cube_coords))
            
    def update_towers(self, aircraft):
        """Update the state of the towers i.e which aircraft belong to which tower.
        """
        
        # For each aircraft get the relative cubic-hex coordinates
        rel_q = ((2./3)* (aircraft.positions[:,0]-self.tower_list[0].offset[0]))/self.tower_list[0].size
        rel_r = (((-1./3)*(aircraft.positions[:,0]-self.tower_list[0].offset[0]))+((np.sqrt(3)/3)*(aircraft.positions[:,1]-self.tower_list[0].offset[1])))/self.tower_list[0].size
        rel_s = -rel_q-rel_r

        coords = axial_round(rel_q,rel_r,rel_s)

        # Get the tower that matches the relative cubic coordinates
        tower_assignments = np.where(np.all(coords[:, np.newaxis, :] == self.tower_idxs, axis=2))[1]

        # Get unique tower assignments
        unique_towers = np.unique(tower_assignments)

        # Assign drones to unique towers
        for t in unique_towers:
            drones = np.where(tower_assignments == t)[0]
            self.tower_list[t].drones = np.empty(len(drones), dtype=int)
            self.tower_list[t].drones[:] = drones

        # Find empty towers
        empty_towers = np.setdiff1d(np.arange(len(self.tower_idxs)), unique_towers)

        # Assign empty drones to empty towers
        for t in empty_towers:
            self.tower_list[t].drones = []
            
            
    def __iter__(self):
        return iter(self.tower_list)

class Tower:
    """The Tower describes a single cell tower and its coverage and bandwith along with a list of drones connected to it.
    These Towers are represented as hexagons and are tiled around some centre tile.
    """
    def __init__(self, q:float, r:float, size:float, offset:(float,float), max_bandwith:int=5, active:bool=True):
        """Initilises a cell tower.

        Args:
            q (float): The q coordinate of the cell tower.
            r (float): the r coordinate of the cell tower.
            size (float): The radius of the circle enclosing the cell tower.
            offset (float,float): The coordinates of the cluster centre this tower belongs to.
            max_bandwith (int, optional): Maximum number of connected drones. Defaults to 5.
            active (bool, optional): The status of if the tower is active. Defaults to True.
        """
        self.cube_coords = self.q,self.r,self.s = (q,r,-q-r)
        self.offset = offset
        self.size = size
        
        self.max_bandwith = max_bandwith
        self.base_usage = 0
        
        self.gradients = gen_gradients(C1, C2, 11)
        
        self.drones = set()
        
        self.poly = Polygon(self.coords)
        
        self.has_hub = False
        self.active=active
    
    @property
    def colour(self) -> hex:
        """This is the current colour the represented hexagon should be.

        Returns:
            hex: The hecadecimal value of the colour.
        """
        return self.gradients[int((self.bandwith_as_percent*100)//10)]
    
    @property
    def n_drones(self) -> int:
        """The number of drones connected to the tower.

        Returns:
            int: The number of drones connected to the tower.
        """
        return len(self.drones)
    
    @property
    def bandwith_as_percent(self) -> float:
        """Returns the availbandwith as a percentage.

        Returns:
            float: The available bandwith
        """
        return max(1-((self.n_drones/self.max_bandwith)+self.base_usage),0)
    
    @property   
    def centre(self)-> (float,float):
        """The centre coordinate of the hexagon in x-y cartesian space.

        Returns:
            (float,float): The (x,y) coordinate of the centre of the hexagon.
        """
        x = self.offset[0] + (self.size*((3/2)*self.q))
        y = self.offset[1] + (self.size * (((sqrt(3)/2)*self.q) + (sqrt(3)*self.r)))
        
        return (x,y)
    
    @property
    def coords(self) -> List[List[float]]:
        """The list of the 6 coordinates that make up the vertices of the hexagon.

        Returns:
            List[List[float]]: A list of 6 coordinates.
        """
        centre = self.centre
        
        return np.asarray([
            [
                centre[0] + (self.size * cos((pi/3) * (i+1))),
                centre[1] + (self.size * (sin((pi/3) * (i+1))))
            ] for i in range(6)
        ])
    
    def drop(self, drone: object):
        """Remove a drone from the tower's influence.

        Args:
            drone (Drone): The drone to try and remove,.
        """
        with contextlib.suppress(Exception):
            self.drones.remove(drone)
    
    def add(self, drone:int):
        """Add drone to the tower influence.

        Args:
            drone (object): The drone to add.
        """
        self.drones.add(drone)
        
    def includes(self, point: Point) -> bool:
        """Check that a point is within the towers influence

        Args:
            point (Point): The point to check.

        Returns:
            bool: If the point is included.
        """
        return self.poly.contains(point)
    
    def update_bandwith(self, thresh:float = 0.7):
        """Set the towers base bandwith usage, this can change over time.

        Args:
            thresh (float, optional): The threshold to change the value. Defaults to 0.8.
        """
        if np.random.rand() > thresh:
            if self.has_hub:
                self.base_usage = np.clip(np.random.normal(0.1,0.1),0,1)
            else:
                self.base_usage = np.clip(np.random.normal(0.2,0.25),0,1)
            
        
        
def create_hex(_hex: Tower, _vec: Tower, size: float, offset: (float,float), max_bandwith:int) -> Tower:
    """Generate a new tower.

    Args:
        _hex (Tower): A reference tower.
        _vec (Tower): The value to distort this by.
        size (float): The radius of the circle that encloses the hexagon.
        offset (float,float): The centre of the cluster that this tower belongs to.
        max_bandwith (int): The maximum number of drones to be connected to this tower.

    Returns:
        Tower: The tower object.
    """
    return Tower(_hex.q + _vec.q, _hex.r+_vec.r,size, offset, max_bandwith=max_bandwith)

def scale(_hex: Tower, factor:float, size:float, offset: (float,float)) -> Tower:
    """Scale the transformation of a Tower.

    Args:
        _hex (Tower): The tower to transform.
        factor (float): The scaling factor.
        size (float): The radius of the circle that encloses the hexagon. 
        offset (float,float): The centre of the cluster that this tower belongs to.

    Returns:
        Tower: The scaled tower object.
    """
    return Tower(_hex.q * factor, _hex.r * factor,size, offset)

def direction_hex(direction:int, size:float, offset:(float,float)) -> Tower:
    """Gets the directional hexagon on one of the 6 faces of an existing hexagon.

    Args:
        direction (int): The direction to get the nex hexagon from.
        size (float): The radius of the circle that encloses the hexagon.
        offset (float,float): The centre of the cluster that this tower belongs to.

    Returns:
        Tower: The directional Tower object.
    """
    if size not in DIRECTION_VECTORS:
        DIRECTION_VECTORS[size] = [
        Tower(+1, 0,size,offset), Tower(+1, -1,size,offset), Tower(0, -1,size,offset), 
        Tower(-1, 0,size,offset), Tower(-1, +1,size,offset),  Tower(0, +1,size,offset), 
        ]
    
    return DIRECTION_VECTORS[size][direction]

def neighbor(_hex:Tower, direction:int, size:float, offset: (float,float),max_signal:List[int]) -> Tower:
    """Gets the neighbor of a Tower in a given direction.

    Args:
        _hex (Tower): The reference Tower.
        direction (int): The direction to get the neighbor in.
        size (float): The radius of the circle that encloses the hexagon.
        offset (float,float): The centre of the cluster that this tower belongs to.
        max_signal (List[int]): A list of maximum signals to randomly choose from.
    
    Returns:
        Tower: The neighbor tower object.
    """
    return create_hex(_hex, direction_hex(direction, size,offset), size, offset, np.random.choice(max_signal))

def hex_ring(centre:Tower, ring: int, size: float, offset:(float,float), max_signal:List[int]) -> List[Tower]:
    """Generate a single ring from a given unit radius from the centre of grid.

    Args:
        centre (Tower): Reference tower.
        ring (int): The ring, radius value.
        size (float): The radius of the circle that encloses the hexagon.
        offset (float,float): The centre of the cluster that this tower belongs to.
        max_signal (List[int]): A list of maximum signals to randomly choose from.

    Returns:
        List[Tower]: The list of Tower objects in this ring.
    """
    results = []

    _hex = create_hex(centre, scale(direction_hex(4, size, offset),ring,size,offset), size, offset, max_bandwith=np.random.choice(max_signal))

    for i, _ in itertools.product(range(6), range(ring)):
        results.append(_hex)
        _hex=neighbor(_hex, i, size, offset,max_signal)

    return results

def ring_to(centre:(float,float), rings:int, size: float, max_signal:List[int]) -> List[Tower]:
    """Generate n rings of towers spiriling out from a given centre.

    Args:
        centre (Tower): The reference centre Tower object.
        rings (int): The number of rings to generate. rings >= 1.
        size (float): The radius of the circle that encloses the hexagon.
        max_signal (List[int]): A list of maximum signals to randomly choose from.

    Returns:
        List[Tower]: The list of Towers in this collection.
    """
    centre = Tower(0,0, size, centre,max_bandwith=np.random.choice(max_signal))
    
    results = [centre]
    
    for k in range(1,rings):
        results.extend(hex_ring(centre, k, size, centre.offset, max_signal))
    
    return results




# print(len(ring_to(Tower(0,0,70,(0,0)), 3, 70)))