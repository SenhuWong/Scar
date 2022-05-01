#First load Mat to get

firstN = 5
from scipy import io
from scipy import linalg
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
cfd_datas = io.loadmat("date0.mat")
print(io.whosmat("date0.mat"))

print(cfd_datas.keys())

state_matrix = cfd_datas['p']
print(state_matrix.shape)

nSnapShot = state_matrix.shape[0]
nX = state_matrix.shape[1]
nY = state_matrix.shape[2]
#Perform an Proper orthogonal decomposition

operating_matrix = state_matrix.reshape(nSnapShot,nX*nY)
print(operating_matrix.shape)

u,s,Vh = linalg.svd(operating_matrix)
#Output the firstN modes.
for i in range(firstN):
    ColumnVec = Vh[i].reshape(nX,nY).T
    plt.imshow(ColumnVec)
    plt.savefig("Mode{}.png".format(i))
#Perform an superposition of u s Vh to get the approximated flow

print(u.shape)
print(s.shape)
print(Vh.shape)
#Now test the mutiply of two matrix:
mat1 = np.array([[1,0],[0,1],[0,0]])
print(mat1.shape)
vec1 = np.array([[0],[1]])
print(vec1.shape)
print(mat1.dot(vec1))

fig,ax = plt.subplots(2,1)

ims = []
ax[0].set_title("CDF result")
ax[1].set_title("First {} mode superposition".format(firstN))
for j in range(nSnapShot):
    im0 = ax[0].imshow(state_matrix[j].T,animated=True)
    MatrixVec = operating_matrix[j]
    super = np.zeros_like(MatrixVec)
    for i in range(firstN):
        ColumnVec = Vh[i]
        imagnitude = sum(ColumnVec * MatrixVec)
        super  = super + ColumnVec * imagnitude
    super = super.reshape(nX,nY).T
    #plt.imshow(super)
    #plt.savefig("Snap{}".format(j))
    im1 = ax[1].imshow(super,animated=True)
    ims.append([im0,im1])


#Generating movie and gif
# ani = animation.ArtistAnimation(fig,ims,interval=150,blit=True, repeat_delay=1000)
# ani.save("movie.mp4")
# ani.save("ani.gif",writer='pillow',fps=10)
#Plot EigenValue related

fig,axes = plt.subplots(1,2)
#Left is the eigenvalue
x_axis = np.arange(138)
axes[0].set_yscale('log')
axes[0].plot(x_axis,s)
axes[0].set_title("Eigen value")

axes[1].set_title("Accumulated Energy")
total_Energy = sum(s*s)
accum_Energy = np.zeros_like(x_axis,dtype=float)

for i in range(0,nSnapShot):
    accum_Energy[i] = accum_Energy[i-1] + float(s[i]*s[i]/total_Energy)
#accum_Energy = accum_Energy/total_Energy

axes[1].plot(x_axis,accum_Energy)

plt.savefig("energy.png")
