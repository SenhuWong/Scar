# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import PIL.Image


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
#This is routine to make the state matrix from pictures
from PIL import Image
import numpy as np
im = Image.open("Good.jpg")
im2 = Image.open("Good.jpg")
im.show()
a = np.asarray(im)
a2 = np.asarray(im2)
print(a.shape)
onedim = np.arange(6)
print(onedim.shape)
b = a.reshape((-1,1))
b2 = a2.reshape((-1,1))
print(b.shape)
b = np.concatenate((b,b2),axis = 1)
print(b.shape)

b2 = b2.reshape((526,801,4))
revImg = PIL.Image.fromarray(b2)
revImg.show()