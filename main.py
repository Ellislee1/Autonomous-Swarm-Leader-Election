from src import UI, Environment,SimUI, InfoUI
import threading
import matplotlib.pyplot as plt
import numpy as np
import pyglet


SCREEN_SIZE = (1200,900)
N_SIMS = 10
N_TASKS = 20
TS = 1/30
PATH = 'out/heat_map'
N_AC = 30
SEED = None

env = Environment(bounds=SCREEN_SIZE,grid_centre=np.array(SCREEN_SIZE)/2, n_tasks=N_TASKS)

# ui = UI(env, screen_size=(SCREEN_SIZE[0], SCREEN_SIZE[1]+35))
ui = SimUI(env, screen_size=(SCREEN_SIZE[0], SCREEN_SIZE[1]+35))
info = InfoUI((400,900), env)

env_thread = threading.Thread(target=env.run_n,args=[N_SIMS, TS, N_AC, N_TASKS, PATH, SEED, ui,info], daemon=True)

env_thread.start()
# ui.run()
# pyglet.clock.schedule_interval(lambda dt: ui.flip(), 1)
pyglet.app.run(1/10)

log = env.stop()
env_thread.join()

fig,axes = plt.subplots(3)

# Plot positions
axes[0].plot(log[:,:,0]/env.scale, log[:,:,1]/env.scale)
axes[0].set_xlim(0,SCREEN_SIZE[0]/env.scale)
axes[0].set_ylim(SCREEN_SIZE[1]/env.scale,0)
axes[0].set_title(f'Positions (Scale={env.scale})')

time_series = np.arange(0,log.shape[0],1)*TS

axes[1].plot(time_series,np.clip(1-((log[:,:,7]+(env.state.flight_time_bounds[-1]-log[:,:,8]))/env.state.flight_time_bounds[-1]),0,1))
axes[1].set_xlim(0,time_series[-1])
axes[1].set_title('Remaining Battery %')

axes[2].plot(time_series,np.clip(log[:,:,8]-log[:,:,7],0, np.inf))
axes[2].set_xlim(0,time_series[-1])
axes[2].set_title('Remaining Flight Time (s)')



plt.show()

log = env.logger

tower_states = np.asanyarray(log.tower_states)

lineObjects = plt.plot(tower_states[:,:,2])
plt.legend(iter(lineObjects), list(range(tower_states.shape[1])))
plt.show()