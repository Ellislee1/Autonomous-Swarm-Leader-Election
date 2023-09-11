import numpy as np

data = np.load('out/no_heatmap/no_heat_map_aircraft_data1.npy', allow_pickle=True)
print(data.shape)

print(data[-1,0,0])

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
print(np.sum(changed,axis=0), np.mean(np.sum(changed,axis=0)))
s = np.sum(changed,axis=0)
w = np.where(s > 0)[0]
s=s[w]
print(np.median(s))

results = []
for i in range(data.shape[1]):
    long = []
    last = -1
    count = 0
    for j in range(data.shape[0]):
        set_ = data[j,i,:]
        
        if set_[2] == last and last != -1:
            count += 1/60
        elif set_[2] != last and count > 0:
            long.append(count)
            count = 0
            last = set_[2]
        else:
            last = set_[2]
    results.append(long)

avg = []
for i in range(len(results)):
    if results[i] != []:
        avg.append(np.mean(results[i]))

print(avg, np.mean(avg))