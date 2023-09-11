import numpy as np
import matplotlib.pyplot as plt
import glob
from tqdm import tqdm

heatmap = 'out/heatmap/'
no_heatmap = 'out/no_heatmap/'

spaces = [heatmap,no_heatmap]

means = []
for space in spaces:
    task_space = list(glob.glob(f'{space}*task*'))

    n_complete = []
    max_len = 0
    for file in tqdm(task_space):
        data = np.load(str(file), allow_pickle=True)
        n_complete.append((data[:,1]-data[:,-1])/data[:,1])
        max_len = max(max_len, len(data[:,1]))

    for i in range(len(n_complete)):
        to_pad = max_len-len(n_complete[i])
    
        if to_pad == 0:
            continue
    

        n_complete[i] = np.append(n_complete[i], [n_complete[i][-1]]*to_pad)

    for run in n_complete:
        plt.plot(run)
    
    means.append(np.median(n_complete,axis=0))
    plt.show()

for i,m in enumerate(means):
    plt.plot(m,label='heatmap' if i == 0 else 'random')

plt.legend()
plt.show()



