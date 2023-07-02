from src import UI, Environment,SimUI, InfoUI
import threading
import matplotlib.pyplot as plt
import numpy as np
import pyglet

SCREEN_SIZE = (1200,900)

env = Environment(bounds=SCREEN_SIZE,grid_centre=np.array(SCREEN_SIZE)/2)

# ui = UI(env, screen_size=(SCREEN_SIZE[0], SCREEN_SIZE[1]+35))
ui = SimUI(env, screen_size=(SCREEN_SIZE[0], SCREEN_SIZE[1]+35))
info = InfoUI((400,900), env)

env_thread = threading.Thread(target=env.run, daemon=True)

env_thread.start()
# ui.run()
# pyglet.clock.schedule_interval(lambda dt: ui.flip(), 1)
pyglet.app.run(1/30)

log = env.stop()
env_thread.join()

fig,axes = plt.subplots(3)

# Plot positions
axes[0].plot(log[:,:,0]/env.scale, log[:,:,1]/env.scale)
axes[0].set_xlim(0,SCREEN_SIZE[0]/env.scale)
axes[0].set_ylim(SCREEN_SIZE[1]/env.scale,0)
axes[0].set_title(f'Positions (Scale={env.scale})')

time_series = np.arange(0,log.shape[0],1)/10

axes[1].plot(time_series,np.clip(1-(log[:,:,7]/log[:,:,8]),0,1))
axes[1].set_xlim(0,time_series[-1])
axes[1].set_title('Remaining Battery %')

axes[2].plot(time_series,np.clip(log[:,:,8]-log[:,:,7],0, np.inf))
axes[2].set_xlim(0,time_series[-1])
axes[2].set_title('Remaining Flight Time (s)')

# axes[1,0].plot(time_series,log[:,:,4]%360)
# axes[1,0].set_xlim(0,time_series[-1])
# axes[1,0].set_title('Headings')

# axes[1,1].plot(time_series,log[:,:,5])
# axes[1,1].set_xlim(0,time_series[-1])
# axes[1,1].set_title('X Accelerations')

# axes[1,2].plot(time_series,log[:,:,6])
# axes[1,2].set_xlim(0,time_series[-1])
# axes[1,2].set_title('Y Accelerations')



plt.show()

log = env.logger

tower_states = np.asanyarray(log.tower_states)

lineObjects = plt.plot(tower_states[:,:,2])
plt.legend(iter(lineObjects), list(range(tower_states.shape[1])))
plt.show()