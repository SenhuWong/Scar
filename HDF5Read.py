import h5py
from enum import Enum
from scipy import linalg
import matplotlib.pyplot as plt
import numpy as np
# These two are unnecessary if we perform on raw elements.
# from scipy import io
# import matplotlib.animation as animation
import time

class VarLoc(Enum):
    UnDefined = 0
    CellCentered = 1
    NodeCentered = 2


class HDF5Loader:
    def __init__(self):
        self.root = None
        self.nBlock:int = 0
        self.nNode = []
        self.nCell = []
        self.nConn = []
        self.nVariables:int = 0
        self.varLocation:VarLoc = VarLoc.UnDefined

        self.nSnapShot:int = 0

        self.curMatrix = None

    # First read the basic parameters of the layout of the database
    def read_params(self, filename):
        self.nBlock = 0
        self.nNode = []
        self.nCell = []
        self.nConn = []

        self.root = h5py.File(filename, 'r')
        print(self.root.keys())
        group_geom = self.root["Geometry"]
        for blockName in group_geom.keys():
            self.nBlock += 1
            cur_block = group_geom[blockName]
            self.nNode.append(cur_block['reservedNodes'].shape[0])
            self.nCell.append(cur_block['reservedCells'].shape[0])
            self.nConn.append(cur_block['VConn'].shape[1])

        group_vars = self.root["Variables"]
        block1_vars = group_vars[list(group_vars.keys())[0]]

        self.nSnapShot = len(block1_vars.keys())
        self.nVariables = block1_vars[list(block1_vars.keys())[0]].shape[0]
        self.varLocation = VarLoc.NodeCentered

    def write_params(self):
        print(self.nBlock)
        print(self.nNode)
        print(self.nCell)
        print(self.nConn)
        print(self.nVariables)
        print(self.varLocation)
        print(self.nSnapShot)

    def output_files(self):
        blocks_coord = []
        blocks_vconn = []
        for i in range(self.nBlock):
            blocks_coord.append(self.root['Geometry/Block'+str(i+1)+'/reservedCoord'])
            blocks_vconn.append(self.root['Geometry/Block'+str(i+1)+'/VConn'])

        for i in range(self.nSnapShot):
            output_name = "Out"+list(self.root['Variables/Block1'].keys())[i]+".dat"
            with open(output_name, 'w') as out:
                out.writelines('TITLE="Tecplot Export"\n')
                out.writelines('VARIABLES = "CoordinateX"\n')
                out.writelines('"CoordinateY"\n')
                for j in range(self.nVariables):
                    out.writelines('"Variable'+str(j)+'"\n')
                for j in range(self.nBlock):
                    out.writelines('ZONE T="plane-0 Step1 Incr 0"\n')
                    n_node = self.nNode[j]
                    n_elem = self.nCell[j]
                    n_conn = self.nConn[j]
                    if n_conn==3:
                        out.writelines("Nodes={}, Elements={},ZONETYPE={}\n".format(n_node,n_elem,'FETRIANGLE'))
                    elif n_conn==4:
                        out.writelines("Nodes={}, Elements={},ZONETYPE={}\n".format(n_node,n_elem,'FEQUADRILATERAL'))
                    out.writelines("DATAPACKING=BLOCK\n")
                    for axis_each in blocks_coord[j]:
                        for node_xyz in axis_each:
                            out.write(str(node_xyz)+"\n")
                    variable_shots = self.root["Variables/Block"+str(j+1)]
                    variable = variable_shots[list(variable_shots.keys())[i]]
                    print(variable.shape)
                    for eachVar in variable:
                        print('each var called\n')
                        for eachValue in eachVar:
                            out.write(str(eachValue)+"\n")
                    for each_conn in blocks_vconn[j]:
                        for each_vert in each_conn:
                            out.write(str(each_vert)+" ")
                        out.write('\n')

    # Do a POD for var_ind th variable
    def form_state_matrix(self, var_ind:int):
        self.nBlock = 1
        if self.nBlock > 1:
            all_var_list = []
            for block in self.root['Variables']:
                block_var_list = []
                cur_blk_group = self.root['Variables'+'/'+block]
                for shot in cur_blk_group:
                    dset = cur_blk_group[shot]
                    block_var_list.append(dset[var_ind,:])
                block_state_matrix = np.stack(block_var_list,1)
                all_var_list.append(block_state_matrix)
            state_matrix = np.concatenate(all_var_list,0)
            print(state_matrix.shape)
            print(type(state_matrix))
            print(state_matrix.dtype)
            return state_matrix
        else:
            block_var_list = []
            cur_blk_group = self.root['Variables' + '/' + list(self.root['Variables'].keys())[0]]
            for shot in cur_blk_group:
                dset = cur_blk_group[shot]
                block_var_list.append(dset[var_ind, :])
            state_matrix = np.stack(block_var_list, 1)
            print(state_matrix.shape)
            print(type(state_matrix))
            print(state_matrix.dtype)
            return state_matrix

    def write_mode(self,u,var_name):
        accum_nnode = np.add.accumulate(np.ndarray(self.nNode))
        block0_share = u[0:accum_nnode[0],:]
        #Write into hdf5 file
        for i in range(1,self.nBlock)
            block_shared = u[accum_nnode[i-1]:accum_nnode[i],:]
        #Write into hdf5 file






    def write_modes(self,filename):
        print('another one bites the dust')


# This class should serve as the actual performer of POD,
# which take the matrix from HDF5Loader and then put the PODed Modes into HDF5Loader into database.
class PODPerformer:
    def __init__(self,hdf_holder:HDF5Loader):
        self.holder = hdf_holder
        self.nFreedom = self.holder.nNode
        self.nShot = self.holder.nSnapShot

    def perform(self,var_list:list):
        nVariable = self.holder.nVariables
        for i in range(1):
            print('it is still running')
            state_matrix = self.holder.form_state_matrix(i)
            u,s,vh = self.svd_decomposition(state_matrix)
            #Decomposition is done, do the projection back
            self.outputModes(self,u)

        print('Not implemented yet')

    def svd_decomposition(self, mat):
        begin = time.time()
        u,s,vh = linalg.svd(mat[0:80000,:])
        end = time.time()
        print(end-begin)
        print("u.shape",u.shape)
        print("s.shape",s.shape)
        print("vh.shape",vh.shape)
        return (u,s,vh)

    # Out put modes into tecplot file format
    # Later this should be handled by HDF5 Reader
    def putToWriter(self,u,s,first_n = 6,first_percent = 0.99, use_percent = True):

    def outputModes(self,u,s,first_n = 6,first_percent = 0.99, use_percent = True):
        if use_percent:
            total = np.sum(np.square(s))
            accum = np.add.accumulate(np.square(s))
            first_n = 0
            for i in range(self.nShot):
                first_n += 1
                if accum>first_percent*total:
                    break
            mode_remain = u[:, 0:first_n]
            mode_eigen =  s[0:first_n]
            var_name = "Var"
            self.holder.write_mode(var_name)
            #We could call a write function here
        else:
            mode_remain = u[:,0:first_n]
            mode_eigen = s[0:first_n]
            #Also a write function here




loader = HDF5Loader()
loader.read_params("unrans.h5")
loader.write_params()
# loader.output_files()
performer = PODPerformer(loader)
performed_varInd = [0,1,2]
performer.perform(performed_varInd)

#
# f = h5py.File('theOnly.h5','r')
# print(list(f.keys()))
#
# group_geometry = f["Geometry"]
# print("Geometry's keys: ", group_geometry.keys())
# print(list(group_geometry.keys())[0])
#
# group_variable = f["Variables"]
# print("Variable's keys: ", group_variable.keys())
#
# group_variable_block0 = group_variable["Block1"]
# print(group_variable_block0.keys())
# print(len(group_variable_block0.keys()))
# print(group_variable_block0['time0'])
#
# geometry_block1 = f["Geometry/Block1"]
# print(geometry_block1.keys())
#
# coord = geometry_block1['reservedCoord']
# print(coord.shape)
# print(coord[0,0:10])
#
# with open("PureGeo",'w') as out:
#     out.writelines('TITLE="Tecplot Export"\n')
#     out.writelines('VARIABLES = "CoordinateX"\n')
#     out.writelines('"CoordinateY"\n')
#     for block in group_geometry.keys():
#         out.writelines('ZONE T="plane-0 Step1 Incr 0"\n')
#
#         cur_block = group_geometry[block]
#         nnode = cur_block['reservedNodes'].shape[0]
#         nelem = cur_block['reservedCells'].shape[0]
#         nConn = cur_block['VConn'].shape[1]
#         if nConn==3:
#             out.writelines("Nodes={}, Elements={},ZONETYPE={}\n".format(nnode,nelem,'FETRIANGLE'))
#         elif nConn==4:
#             out.writelines("Nodes={}, Elements={},ZONETYPE={}\n".format(nnode,nelem,'FEQUADRILATERAL'))
#         out.writelines("DATAPACKING=BLOCK\n")
#         for eachXYZ in cur_block['reservedCoord']:
#             for nodeXYZ in eachXYZ:
#                 out.writelines(str(nodeXYZ))
#                 out.write('\n')
#
#         for eachConn in cur_block['VConn']:
#             for eachVert in eachConn:
#                 out.write(str(eachVert))
#                 out.write(" ")
#             out.write('\n')
#
#
#         print(nnode,nelem,nConn)
