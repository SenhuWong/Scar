
#We only use the first 50 snapshot perform svd

filename = "date0.mat"
firstNSnapshot = 137
r = 5
r = min(r,firstNSnapshot)
from scipy import io
from scipy import linalg
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import math
raw_data = io.loadmat(filename)
print(io.whosmat(filename))
print(raw_data.keys())
dt = raw_data['dt'][0]
print(dt)

#Test python slice
test = np.array([[1,0],[0,2],[1,1]])

slice = test[0:2]
print(type(slice))
print(test.shape)
#Fetch First several snapshot
state_matrix = raw_data['p']
nSnapShot = state_matrix.shape[0]
nX = state_matrix.shape[1]
nY = state_matrix.shape[2]
operating_matrix = state_matrix.reshape(nSnapShot,nX*nY)

X = operating_matrix[0:firstNSnapshot].T
X1 = operating_matrix[1:firstNSnapshot+1].T
print(operating_matrix.shape)

#Since DMD needs transpose anyway, I do a transpose here regardless of time cost.
u,s,Vh = linalg.svd(X,full_matrices=False)
U_r = u[:,0:r]#First r column of U
S_r = np.diag(s[0:r])#First r eigen
V_r = Vh.T[:,0:r]#First r colume of V
print(U_r.shape)
print(S_r.shape)
print(V_r.shape)

Atilde = U_r.T.dot(X1).dot(V_r).dot(linalg.inv(S_r))
print(Atilde.shape)

val,W_r = linalg.eig(Atilde,right=True)
print("Val:",val)
print(W_r.shape)
print(W_r)
print(Atilde)
#print((W_r.dot(np.diag(val)).dot(linalg.inv(W_r))).astype(np.float32))
Phi = X1.dot(V_r).dot(linalg.inv(S_r)).dot(W_r)
print(Phi.dtype)
print(Phi[:,0].shape)

b = linalg.pinv(Phi).dot(X[:,0])
print(b)

#Now for any given t,we could compute

t_slice = np.linspace(0,nSnapShot*dt,4*nSnapShot+1)
print(Phi.shape)
print(b.shape)
print(val.shape)
print(type(val))
diag_omega = np.diag(np.exp(np.log(val)/dt))

# print(np.exp(diag))


continum_eigval = np.log(val)/dt

#Trying to make it animated.
fig,axes = plt.subplots(2,1)
ims = []
axes[0].set_title("Raw data")
axes[1].set_title("DMD Advances")
#I should make an animation here.
for i in range(2*nSnapShot-1):
    im0 = axes[0].imshow(state_matrix[i//2].T, animated=True)
    cur_time = t_slice[i]
    print(cur_time)
    #For current time, the X could be given by:
    dmd_result = Phi.dot(np.diag(np.exp(continum_eigval*cur_time))).dot(b).real
    dmd_result = dmd_result.reshape(nX,nY).T
    im1 = axes[1].imshow(dmd_result, animated=True)
    ims.append([im0,im1])

ani = animation.ArtistAnimation(fig,ims,interval=150,blit=True, repeat_delay=1000)
ani.save("dmd.mp4")
ani.save("dmd.gif",writer='pillow',fps=10)

print('end of a dmd routine')







# print('type of u:',u.dtype)
# print('type of s:',s.dtype)
# print('type of Vh:',Vh.dtype)
# print(np.diag(s))
# print(np.diag(1/s))
# print("----------------------------")
# print(u.T.shape)
# print(X1.shape)
# print(Vh.T.shape)
# A_scratch = u[:,0:rank].T.dot(X1).dot(Vh[0:rank,:].T).dot(np.diag(1/s[0:rank]))
# print("print A_scratch's type:",A_scratch.dtype)
#
# la,W_r = linalg.eig(A_scratch,right=True)
# print(la)
# print(W_r)
#
# Phi = X1.dot(Vh[0:rank,:].T).dot(np.diag(1/s[0:rank])).dot(W_r)
# print('Shape of Phi:',Phi.shape)
# print("Type of Phi:",Phi.dtype)
# omega = np.log(la)
# b = linalg.pinv(Phi).dot(X[:,0])
# print(b)
# #Assertion Here:
# print("Assertion made here:")
# print("la's shape",la.shape)
# print(la)
# print("v's shape",W_r.shape)
# print(A_scratch.dot(W_r))
# print(W_r.dot(np.diag(la)))
# time_dynamics = np.zeros((rank,1000),dtype=float)
# print(time_dynamics.shape)
# print(time_dynamics[:,0].shape)
# print(b.shape)
# time_dynamics[:,0] = b
# #Check the result of eigen value and eigen vector
# print(np.diag(la).shape)
# for i in range(1,1000):
#     time_dynamics[:,i] = np.diag(la).dot(time_dynamics[:,i-1])
#
# for i in range(1,10):
#     real_time_dynamics = Phi.dot(time_dynamics[:,i])
#     print(real_time_dynamics)
#
#
#
# # matrix = np.array([[1,2],[3,4]])
# # la,v = linalg.eig(matrix,right=True)
# #
# #
# #
# #
# # print(la)
# # print(v)
# # print(v.T)
# # print(v.T.dot(v))
# # print(v.dot(v.T))
# # print(v.T.dot(la).dot(v))
# # print(v.dot(np.diag(la)).dot(linalg.inv(v)))
# # print('A_scratch',A_scratch.shape)
# # print('u:',u.shape)
# # print('s',s.shape)
# # print('Vh',Vh.shape)
