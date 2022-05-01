from scipy import io
import numpy as np
from scipy import linalg
from PIL import Image
import matplotlib.pyplot as plt
matlab_data = io.loadmat("date0.mat")
print(io.whosmat("date0.mat"))
#[('dt', (1, 1), 'double'), ('m', (1, 1), 'double'), ('nr', (1, 1), 'double'), ('nt', (1, 1), 'double'), ('nx', (1, 1), 'double'), ('p', (138, 100, 20), 'double'), ('r', (100, 20), 'double'), ('x', (100, 20), 'double')]
print(matlab_data.keys())
#dict_keys(['__header__', '__version__', '__globals__', 'dt', 'm', 'nr', 'nt', 'nx', 'p', 'r', 'x'])
operating_matrix = matlab_data['p']
nSnapShot = operating_matrix.shape[0]
nX = operating_matrix.shape[1]
nY = operating_matrix.shape[2]

#First let's plot for time0 of the original data
curPMatrix = operating_matrix[137]
pmax = np.max(curPMatrix)
pmin = np.min(curPMatrix)
print("max is",pmax)
print("min is",pmin)
# for i in range(0,100):
#     for j in range(0,20):
#         if(curPMatrix[i][j]>pmax or curPMatrix[i][j]<0.1):
#             print("ERROR")
# curPMatrix = curPMatrix*255/(pmax-pmin)

print('shape of time 0 is ',curPMatrix.shape)
plt.imshow(curPMatrix.T,cmap = 'gray')
plt.show()


#End of that
print(nX,nY)
print(matlab_data['r'][0][1:10])
print(matlab_data['x'][0][1:10])

operating_matrix=operating_matrix.reshape(nSnapShot,nX*nY)
print(operating_matrix.shape)

u,s,Vh = linalg.svd(operating_matrix)
#First let's check how much energy is captured within the first 20

all = 0
for i in range(0,s.shape[0]):
    all += s[i]*s[i]
first20 = 0
for i in range(0,5):
    first20 += s[i]*s[i]
print("First 20's L2 square percentage is ",first20/all)
max = -1
for i in range(0,5):
    ColumeVec = Vh[i]
    for j in range(0,nX*nY):
        if (Vh[i][j]>max):
            max = Vh[i][j]
    print(i,max)
coefficient = 255/(1.01*max)

for i in range(0,6):
    ColumeVec = Vh[i].reshape(nX,nY).T
    plt.matshow(ColumeVec)
    plt.savefig("Mode{}".format(i))
    #revImg = Image.fromarray(ColumeVec)
    #revImg.show()

#Now we have the first 6 modes that are dominating,we could store them

