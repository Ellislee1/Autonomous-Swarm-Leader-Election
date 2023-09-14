import numpy as np
import matplotlib.pyplot as plt
import glob
from tqdm import tqdm

heatmap = 'out/heatmap/'
no_heatmap = 'out/no_heatmap/'
heatmap_p7 = 'out/heatmap_p7/'
no_heatmap_p7 = 'out/no_heatmap_p7/'
heatmap_active_p7 = 'out/heatmap_active_only_p7/'
heatmap_active = 'out/heatmap_active_only/'

heatmap_towers = 'out/heatmap_towers/'
no_heatmap_towers = 'out/no_heatmap_towers/'
heatmap_unfiltered_towers = 'out/heatmap_unfiltered_towers/'
heatmap_p7_towers = 'out/heatmap_p7_towers/'
no_heatmap_p7_towers = 'out/no_heatmap_p7_towers/'
heatmap_unfiltered_p7_towers = 'out/heatmap_unfiltered_p7_towers/'
colours = ['b','r', 'c', 'm', 'b:', 'c:']

spaces = [heatmap,no_heatmap, heatmap_p7, no_heatmap_p7, heatmap_active,heatmap_active_p7]
labels = ['heatmap - filtered', 'no heatmap', 'heatmap - filtered 0 Start','no heatmap 0 Start', 'heatmap - unfiltered', 'heatmap - unfiltered 0 Start']
# spaces = [heatmap_towers, no_heatmap_towers, heatmap_p7_towers, no_heatmap_p7_towers, heatmap_unfiltered_towers,heatmap_unfiltered_p7_towers]


means = []
for space in spaces:
    task_space = list(glob.glob(f'{space}*task*'))

    n_complete = []
    max_len = 0
    for file in tqdm(task_space):
        data = np.load(str(file), allow_pickle=True)

        
        v = (data[:,1]-data[:,-1])/(data[:,1]+1e-10)
        v[np.where(data[:,1]==0)[0]] = 0
        
        # v = data[:,1]-data[:,-1]
        
        n_complete.append(v)
        max_len = max(max_len, len(data[:,1]))

    for i in range(len(n_complete)):
        to_pad = max_len-len(n_complete[i])
    
        if to_pad == 0:
            continue
    

        n_complete[i] = np.append(n_complete[i], [n_complete[i][-1]]*to_pad)

    # for run in n_complete:
    #     plt.plot(run)
    
    means.append(np.mean(n_complete,axis=0))
    # plt.show()

for i,m in enumerate(means):
    len_ = np.array(list(range(len(m))))*(1/30)
    plt.plot(len_,m,colours[i],label=labels[i])

# plt.title('Comparison of Completed Tasks in Fluctuating Signal Environment')
plt.title('Comparison of Heatmap Utilisation in Static-Cell Environment')
plt.xlabel('Sim Time (s)')
# plt.ylabel('# Complete Tasks (Avg.)')
plt.ylabel('Ratio of Completed tasks (Avg.)')
plt.legend()
plt.show()



