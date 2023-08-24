import numpy as np

data = np.load('out/seed_test_run3.npy', allow_pickle=True)
print(data.shape)

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
print(np.mean(s))