import numpy as np
import glob
from tqdm import tqdm


age_ring = 'out/age_ring_2/'
ours = 'out/heatmap_p7_towers/'
ours2 = 'out/2IC_10-1/'
random = 'out/random/'

# age_ring = 'out/age_ring_static/'
# ours = 'out/2ic10-5-static/'
# ours2 = 'out/2ic5-10-static/'
# random = 'out/random_static/'

# spaces = [ours, ours2, age_ring, random]
spaces = [ours,ours2, age_ring,random]

means = []
for space in tqdm(spaces):
    paths = list(glob.glob(f'{space}*aircraft*'))

    paths = [a for a in paths if 'heuristics' not in a]

    m1 = []
    for path in paths:
        h = []
        data = np.load(path, allow_pickle=True)

        # print(data.shape)
        # print(data[-1,0,0])

        changed = []

        for i in range(1, len(data)):
            ts = []
            for k, tower in enumerate(data[i]):
                if tower[2] == data[i-1,k,2]:
                    ts.append(0)
                else:
                    ts.append(1)
            changed.append(ts)

        changed = np.array(changed)

        s=np.sum(changed,axis=0)
        w = np.where(s > 0)[0]
        s=s[w]

        h.append(np.mean(s))

        result = []
        for i in range(data.shape[1]):
            last = -1
            count = 0
            tower_age = 0
            prev_active = False
            ages = []
            # loop through each iteration for a single tower
            for j in range(data.shape[0]):
                set_ = data[j,i,:]
                if set_[-1] == 1 and prev_active == False:
                    prev_active = True
                    tower_age = 1/30
                elif set_[-1] == 1 and prev_active == True:
                    tower_age += 1/30
                elif set_[-1] == 0:
                    prev_active = False

                if last == -1 and set_[2] > -1 and prev_active:
                    last = set_[2]
                    count = 1/30
                    tower_age = 1/30
                elif last != -1 and last == set_[2] and prev_active:
                    count += 1/30
                elif last != set_[2] or prev_active == False:
                    
                    if last > -1:
                        ages.append(count/tower_age)


                    if prev_active == False:
                        last = -1
                        count = 0
                    else:
                        last = set_[2]
                        count = 0

            if len(ages) > 0:
                result.append( np.mean(ages))

        avg = [np.mean(result)]
        h.append(np.mean(avg))

        m1.append(h)

    means.append(np.mean(m1, axis=0))

print('# changes','Avg relative age')
print(means)


# data = np.load('out/age_ring/age_ring_aircraft_data1.npy', allow_pickle=True)
# print(data.shape)

# print(data[-1,0,0])

# changed = []
# for i in range(1, len(data)):
#     ts = []
#     for k, tower in enumerate(data[i]):
#         if tower[2] == data[i-1,k,2]:
#             ts.append(0)
#         else:
#             ts.append(1)
#     changed.append(ts)

# changed = np.array(changed)
# print(np.sum(changed,axis=0), np.mean(np.sum(changed,axis=0)))
# s = np.sum(changed,axis=0)
# w = np.where(s > 0)[0]
# s=s[w]
# print(np.median(s))

# results = []
# for i in range(data.shape[1]):
#     long = []
#     last = -1
#     count = 0
#     for j in range(data.shape[0]):
#         set_ = data[j,i,:]
        
#         if set_[2] == last and last != -1:
#             count += 1/60
#         elif set_[2] != last and count > 0:
#             long.append(count)
#             count = 0
#             last = set_[2]
#         else:
#             last = set_[2]
#     results.append(long)

# avg = []
# for i in range(len(results)):
#     if results[i] != []:
#         avg.append(np.mean(results[i]))

# print(avg, np.mean(avg))