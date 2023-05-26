from src.environment import Environment

e = Environment(screen_size = (900,900),n_rings=2, hex_size=150, n_drones=5, max_signal=[10,15])

e.run()