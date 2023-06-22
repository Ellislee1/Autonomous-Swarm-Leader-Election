from src.environment import Environment

e = Environment(screen_size = (900,900),n_rings=5, hex_size=70, n_drones=20, max_signal=[10,15])

e.run()