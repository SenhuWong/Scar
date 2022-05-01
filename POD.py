#This class aims at using scipy's utility to perform a singular value decomposition.
#It should contain:
#1.Read Input from a series of files(maybe an RGB picture for now) and form into a matrix
#2.Perform Singular Value Decomposition with scipy
#3.Output U and A and V of the first (user_specified) modes
#This abstract base class should read from a file given channel,freedom and timeShots
import PIL.Image
import numpy
import numpy as np
import scipy
from scipy import linalg
from PIL import Image

class PodReader:
    def __init__(self, n_channel: int, n_freedom: int, n_time_shot: int):
#Given channel,freedom and timeshot we could read from a file and form the matrix
        self.n_channel: int = n_channel
        self.n_freedom: int = n_freedom
        self.n_timeShot: int = n_time_shot
        self.formed_matrix = None

    def read(self,filenames):
        #For now it's a pillow reader
        for filename in filenames:
            image = Image.open(filename)
            column = np.asarray(image)




        
        
        #self.formed_matrix = np.ndarray
        return

    def get_matrix(self):
        return self.formed_matrix


class SVDHandler:
    def __init__(self, reader: PodReader):
        self.matrix:numpy.ndarry = reader.get_matrix()
        self.m, self.n = self.matrix.shape
        self.U = None
        self.s = None
        self.Vh = None

    def perform_svd(self):
        self.U, self.s, self.Vh = linalg.svd(self.matrix)

    def get_u(self):
        return self.U

    def get_vh(self):
        return self.Vh


class PodWriter:
    def __init__(self, holder: SVDHandler):
        self.holder = holder

    def write(self):
        return


