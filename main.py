from src.environment import Environment

e = Environment(n_rings=6, hex_size=50, n_drones=200, max_signal=[10,15])

e.run()