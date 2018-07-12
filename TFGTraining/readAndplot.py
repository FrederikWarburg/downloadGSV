import numpy as np
import matplotlib.pyplot as plt


file = open("/Users/frederikwarburg/Desktop/loss.txt")

index = []
loss = []
n = len("CurrentIndex ")
m = len("  7172  Loss =  ")
for line in file:

    if line[:n] == "CurrentIndex ":
        idx = line.find("/")
        print(line[n:idx])
        index.append(int(line[n:idx]))
        loss.append(np.float64(line[(idx+m):]))

plt.plot(index,loss,'-o')
N = 100
mean = np.convolve(np.array(loss), np.ones((N,))/N, mode='valid')
plt.plot(np.linspace(0,index[-1],len(mean)),mean,'r-o')
plt.legend(['loss per batch','running mean of loss per 100 batch'])
plt.show()