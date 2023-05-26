from matplotlib.colors import to_rgb
import numpy as np

from typing import List

def gen_gradients(c1:hex,c2:hex,n:int) -> List[hex]:
    """Generate a list of n gradient colours.

    Args:
        c1 (hex): The starting colour.
        c2 (hex): The target colour.
        n (int): The number of colours to generate.

    Returns:
        List[hex]: A list of n generated colours for the gradient.
    """
    c1_rgb = np.array(to_rgb(c1))/255
    c2_rgb = np.array(to_rgb(c2))/255
    mix_pcts = [x/(n-1) for x in range(int(n))]
    rgb_colors = [((1-mix)*c1_rgb + (mix*c2_rgb))*255 for mix in mix_pcts]
    return [
        "#" + "".join([format(int(round(val * 255)), "02x") for val in item])
        for item in rgb_colors
    ]