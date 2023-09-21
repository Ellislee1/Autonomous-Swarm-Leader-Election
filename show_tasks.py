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

# age_ring = 'out/age_ring_static/'
# ours = 'out/2ic10-5-static/'
# ours2 = 'out/2ic5-10-static/'
# random = 'out/random_static/'

age_ring = 'out/age_ring_2/'
ours = 'out/heatmap_p7_towers/'
ours2 = 'out/2IC_10-1/'
random = 'out/random/'

# spaces = [ours, ours2, age_ring, random]
# spaces = [ours,ours2, age_ring,random]




dump1 = 'out/dump1/'
dump2 = 'out/dump2/'
dump3 = 'out/dump3/'
dump4 = 'out/dump4/'

colours = ['b','c', 'r', 'b:', 'c:', 'r:']

# spaces = [heatmap, no_heatmap, heatmap_p7, no_heatmap_p7, heatmap_active,heatmap_active_p7]
# spaces = [heatmap,heatmap_active,no_heatmap,heatmap_towers,heatmap_unfiltered_towers,no_heatmap_towers]
# spaces = [heatmap_p7,heatmap_active_p7,no_heatmap_p7,heatmap_p7_towers,heatmap_unfiltered_p7_towers,no_heatmap_p7_towers]
spaces = [ours, ours2, age_ring, random]
# spaces = [dump1, dump2, dump3]
# labels = ['dump1','dump2','dump3','dump4']
# labels = ['heatmap - exploitation', 'heatmap - exploration', 'no heatmap', 'heatmap - exploitation (unstable)', 'heatmap - exploration (unstable)', 'no heatmap (unstable)']
labels = ['Ours bat', 'Ours dist', 'ring']
# spaces = [heatmap_towers, no_heatmap_towers, heatmap_p7_towers, no_heatmap_p7_towers, heatmap_unfiltered_towers,heatmap_unfiltered_p7_towers]
# labels = ['Ours','Ours2','Age Ring', 'Random']

means = []
for space in spaces:
    task_space = list(glob.glob(f'{space}*task*'))

    n_complete = []
    max_len = 0
    for file in tqdm(task_space):
        data = np.load(str(file), allow_pickle=True)

        
        # v = (data[:,1]-data[:,-1])/(data[:,1]+1e-10)
        # v[np.where(data[:,1]==0)[0]] = 0
        
        v = data[:,1]-data[:,-1]
        
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
means=np.array(means)

for i,m in enumerate(means):
    len_ = np.array(list(range(len(m))))*(1/30)
    print(m[-1])
    plt.plot(len_,m,colours[i],label=labels[i])

plt.title('Number of Completed Tasks without Initial Tasks')
# plt.title('Task Completion Percentage without Initial Tasks')
plt.xlabel('Sim Time (s)')
plt.ylabel('# Complete Tasks (Avg.)')
# plt.ylabel('Percentage of Completed tasks (Avg.)')
plt.legend()
plt.show()



