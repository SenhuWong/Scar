#include <iostream>
#include <fstream>
#include <vector>
#include "hdf5.h"
#include <set>
//#include <sys/io.h>
#include <sys/stat.h>
#include <dirent.h>
#include <unistd.h>
#include <sys/types.h>
// struct _finddata_t
// {
//     unsigned attrib;
//     time_t time_create;
//     time_t time_access;
//     time_t time_write;
//     size_t size;
//     char name[260];
// };

const int NBLOCKS=2;
//We should create two types of database
//One for storing geometry, another for storing variables
enum PackType
{
    NoneType = -1,
    FETRIANGLE = 1,
    FEQUADRILATERAL = 2,
};
template<int nblock>
struct Tecplot_MetaData
{
    int textLines[nblock];
    int n_allNodes[nblock];
    int n_allElems[nblock];
    int n_coords;
    int n_vars;
    PackType types[nblock];
    
    bool is_packed;
    double xmax[3];
    double xmin[3];
    int abandoned_axis = -1;
    Tecplot_MetaData(int ntext[nblock],int nnode[nblock],int nelem[nblock],int ncoord,int nvar, bool pack,double maxs[3],double mins[3], int unind,PackType ptp[nblock])
    :n_coords(ncoord),n_vars(nvar),is_packed(pack)
    {
        for(int i = 0;i<nblock;i++)
        {
            textLines[i] = ntext[i];
            n_allNodes[i] = nnode[i];
            n_allElems[i] = nelem[i];
            types[i] = ptp[i];
        }
        abandoned_axis = unind;
        for(int i = 0;i<3;i++)
        {
            xmax[i] = maxs[i];
            xmin[i] = mins[i];
        }
    }
};
template<int nblock>
class HDF_writer
{
    std::string d_rootfilename;
    std::vector<std::string> d_vardb_names;
    std::string d_geomdb_name;
    Tecplot_MetaData<nblock>* d_meta;

public:
    HDF_writer(Tecplot_MetaData<nblock>& metaData)
    {
        d_meta = &metaData;
    }
    void readGeometry(const std::string& filename)
    {
        d_geomGroupId = H5Gcreate2(d_fileId,"/Geometry",H5P_DEFAULT,H5P_DEFAULT,H5P_DEFAULT);
        d_varGroupId = H5Gcreate2(d_fileId,"/Variables",H5P_DEFAULT,H5P_DEFAULT,H5P_DEFAULT);
        herr_t status;
        status = H5Gclose(d_varGroupId);


        

        std::ifstream fin;
        fin.open(filename);
        char unused_line[100];
        std::set<int,std::less<int>>* abandoned_nodes = new std::set<int,std::less<int>>[nblock];
        std::set<int,std::less<int>>* reserved_cells = new std::set<int,std::less<int>>[nblock];
        int nreservedNodes[nblock];
        double* reserved_node_coordinates[nblock];
        for(int i = 0;i<nblock;i++)
        {
            std::string blockgroup_name = "/Geometry/Block"+std::to_string(i+1);
            std::string blockdataset_name;
            hid_t blockgroup_id = H5Gcreate2(d_fileId,blockgroup_name.c_str(),H5P_DEFAULT,H5P_DEFAULT,H5P_DEFAULT);
            hid_t dataspace_id;
            hid_t dataset_id;

            for(int j = 0;j<d_meta->textLines[i];j++)
            {
                fin.getline(unused_line,100);
            }
            std::cout<<unused_line<<'\n';

            int abandoned_ind = d_meta->abandoned_axis;
            double abandoned_axis_loc;//Find the location of the abandoned_axis_loc

            double unused_double = 0;        
            for(int j = 0;j<d_meta->n_coords;j++)
            {
                if(j==d_meta->abandoned_axis)
                {
                    for(int k = 0;k<d_meta->n_allNodes[i];k++)
                    {
                        fin>>unused_double;
                    }
                    abandoned_axis_loc = unused_double;
                }
                else
                {
                    for(int k = 0;k<d_meta->n_allNodes[i];k++)
                    {
                        fin>>unused_double;
                        if(unused_double>d_meta->xmax[j] or unused_double<d_meta->xmin[j])
                        {
                            abandoned_nodes[i].insert(k+1);
                        }
                    }
                }
                std::cout<<unused_double<<'\n';
            }

        //Here we got all the nodes to abandon
            nreservedNodes[i] = d_meta->n_allNodes[i] - abandoned_nodes[i].size();

            //At this point, we can write down the node to reserve
            int* to_reserve_node = new int[nreservedNodes[i]];
            int temp_int = 0;
            for(int j = 1;j<d_meta->n_allNodes[i]+1;j++)
            {
                if(abandoned_nodes[i].find(j)==abandoned_nodes[i].end())//Not in abandoned nodes
                {
                    to_reserve_node[temp_int++] = j;
                }
            }
            if(temp_int!=nreservedNodes[i])
            {
                std::cout<<i<<" th block"<<temp_int<<"vs"<<nreservedNodes[i]<<"vs"<<abandoned_nodes[i].size()<<'\n';
                throw std::runtime_error("Not compatible nreserve\n");
            }
            hsize_t dim[1] = {nreservedNodes[i]};
            dataspace_id = H5Screate_simple(1,dim,NULL);
            blockdataset_name = blockgroup_name + "/reservedNodes";

            dataset_id = H5Dcreate2(d_fileId,blockdataset_name.c_str(),H5T_STD_I32BE,dataspace_id,H5P_DEFAULT,H5P_DEFAULT,H5P_DEFAULT);
            status = H5Dwrite(dataset_id,H5T_NATIVE_INT,H5S_ALL,H5S_ALL,H5P_DEFAULT,to_reserve_node);
            status = H5Sclose(dataspace_id);
            status = H5Dclose(dataset_id);

            

            delete[] to_reserve_node;


            if(d_meta->abandoned_axis!=-1)
            {
                reserved_node_coordinates[i]= new double[(d_meta->n_coords-1)*d_meta->n_allNodes[i]];
            }
            else
            {
                reserved_node_coordinates[i] = new double[d_meta->n_coords*d_meta->n_allNodes[i]];
            }
            for(int j = 0 ;j<d_meta->n_vars;j++)
            {
                for(int k = 0;k<d_meta->n_allNodes[i];k++)
                {
                    fin>>unused_double;
                }
                std::cout<<unused_double<<"\n";
            }
            std::cout<<"End of the variables :"<<unused_double<<'\n';
            int inode[8];
            int nnode = 0;
            switch (d_meta->types[i])
            {
                case PackType::FETRIANGLE:
                    nnode = 3;
                    break;
                case PackType::FEQUADRILATERAL:
                    nnode = 4;
                    break;
                default:
                    break;
            }
            
            for(int k = 0;k<d_meta->n_allElems[i];k++)
            {
                bool isInside = true;
                for(int j = 0;j<nnode;j++)
                {
                    fin>>inode[j];
                    if(abandoned_nodes[i].find(inode[j])!=abandoned_nodes[i].end())
                    {
                        isInside = false;
                    }
                }
                //std::cout<<inode[0]<<','<<inode[1]<<','<<inode[2]<<'\n';
                if(isInside)
                {
                    reserved_cells[i].insert(k+1);
                }
            }
            temp_int = 0;
            int* to_reserve_cell = new int[reserved_cells[i].size()];
            for(auto iter = reserved_cells[i].begin();iter!=reserved_cells[i].end();iter++)
            {
                to_reserve_cell[temp_int++] = *iter;
            }
            dim[0] = reserved_cells[i].size();
            dataspace_id = H5Screate_simple(1,dim,NULL);
            blockdataset_name = blockgroup_name + "/reservedCells";
            dataset_id = H5Dcreate2(d_fileId,blockdataset_name.c_str(),H5T_STD_I32BE,dataspace_id,H5P_DEFAULT,H5P_DEFAULT,H5P_DEFAULT);
            
            status = H5Dwrite(dataset_id,H5T_NATIVE_INT,H5S_ALL,H5S_ALL,H5P_DEFAULT,to_reserve_cell);
            
            status = H5Sclose(dataspace_id);
            status = H5Dclose(dataset_id);
            std::cout<<"ENd of that is "<<inode[0]<<','<<inode[1]<<","<<inode[2]<<","<<inode[3]<<'\n';
            
            
        
        }
        fin.close();
        fin.open(filename);
        for(int i = 0;i<nblock;i++)
        {
            std::string blockgroup_name = "/Geometry/Block"+std::to_string(i+1);
            std::string blockdataset_name;

            hid_t dataspace_id;
            hid_t dataset_id;

            for(int j = 0;j<d_meta->textLines[i];j++)
            {
                fin.getline(unused_line,100);
            }
            std::cout<<unused_line<<'\n';

            int abandoned_ind = d_meta->abandoned_axis;
            double abandoned_axis_loc;//Find the location of the abandoned_axis_loc

            double unused_double = 0;        
            int temp_int = 0;
            for(int j = 0;j<d_meta->n_coords;j++)
            {
                auto iter = abandoned_nodes[i].begin();
                if(j==d_meta->abandoned_axis)
                {
                    for(int k = 0;k<d_meta->n_allNodes[i];k++)
                    {
                        fin>>unused_double;
                    }
                    abandoned_axis_loc = unused_double;
                }
                else
                {
                    
                    for(int k = 0;k<d_meta->n_allNodes[i];k++)
                    {
                        
                        fin>>unused_double;
                        if(k==*iter -1 )
                        {
                            iter++;
                        }
                        else
                        {
                            reserved_node_coordinates[i][temp_int++] = unused_double;
                        }
                    }
                }
                std::cout<<unused_double<<'\n';
            }
            int qstride = abandoned_ind >0 ?2 :3;
            if(temp_int!=qstride*nreservedNodes[i])
            {
                std::cout<<temp_int<<" vs "<<nreservedNodes[i]*qstride<<'\n';
                std::cin.get();
            }
            //At this point, we can write down the node to reserve
            
            hsize_t dim[2] = {qstride,nreservedNodes[i]};

            dataspace_id = H5Screate_simple(2,dim,NULL);
            blockdataset_name = blockgroup_name + "/reservedCoord";

            dataset_id = H5Dcreate2(d_fileId,blockdataset_name.c_str(),H5T_NATIVE_DOUBLE,dataspace_id,H5P_DEFAULT,H5P_DEFAULT,H5P_DEFAULT);
            status = H5Dwrite(dataset_id,H5T_NATIVE_DOUBLE,H5S_ALL,dataspace_id,H5P_DEFAULT,reserved_node_coordinates[i]);
            status = H5Sclose(dataspace_id);
            status = H5Dclose(dataset_id);
            delete[] reserved_node_coordinates[i];


        
            for(int j = 0 ;j<d_meta->n_vars;j++)
            {
                for(int k = 0;k<d_meta->n_allNodes[i];k++)
                {
                    fin>>unused_double;
                }
                std::cout<<unused_double<<"\n";
            }
            std::cout<<"End of the variables :"<<unused_double<<'\n';
            int inode[8];
            int nnode = 0;
            switch (d_meta->types[i])
            {
                case PackType::FETRIANGLE:
                    nnode = 3;
                    break;
                case PackType::FEQUADRILATERAL:
                    nnode = 4;
                    break;
                default:
                    break;
            }
            
            
            temp_int = 0;
            int* to_reserve_cell = new int[reserved_cells[i].size()];
            for(auto iter = reserved_cells[i].begin();iter!=reserved_cells[i].end();iter++)
            {
                to_reserve_cell[temp_int++] = *iter;
            }
            dim[0] = reserved_cells[i].size();
            dim[1] = nnode;
            int* global2Local = new int[d_meta->n_allNodes[i]];
            auto iter = abandoned_nodes[i].begin();
            temp_int = 0;
            for(int k = 0;k<d_meta->n_allNodes[i];k++)
            {
                if(k==*iter -1)
                {
                    global2Local[k] = -1;
                    iter++;                    
                }
                else
                {
                    global2Local[k] = ++temp_int;
                }
            }
            if(temp_int!=d_meta->n_allNodes[i] - abandoned_nodes[i].size())
            {
                std::cout<<"Something wrong\n";
                std::cin.get();
            }
            iter = reserved_cells[i].begin();
            int* to_reserve_vconn = new int[reserved_cells[i].size()*nnode];
            temp_int = 0;
            for(int k = 0;k<d_meta->n_allElems[i];k++)
            {
                if(k==*iter-1)
                {
                    for(int j = 0;j<nnode;j++)
                    {
                        fin>>inode[j];
                        to_reserve_vconn[temp_int++] =  global2Local[inode[j]-1];
                    }
                    iter++;
                }
                else
                {
                    for(int j = 0;j<nnode;j++)
                    {
                        fin>>inode[j];
                    }
                }
            }
            dataspace_id = H5Screate_simple(2,dim,NULL);
            blockdataset_name = blockgroup_name + "/VConn";
            dataset_id = H5Dcreate2(d_fileId,blockdataset_name.c_str(),H5T_STD_I32BE,dataspace_id,H5P_DEFAULT,H5P_DEFAULT,H5P_DEFAULT);
            
            status = H5Dwrite(dataset_id,H5T_NATIVE_INT,H5S_ALL,H5S_ALL,H5P_DEFAULT,to_reserve_vconn);
            
            status = H5Sclose(dataspace_id);
            status = H5Dclose(dataset_id);
            std::cout<<"ENd of that is "<<inode[0]<<','<<inode[1]<<","<<inode[2]<<","<<inode[3]<<'\n';
        }
        fin.close();
        
        
        status = H5Gclose(d_geomGroupId);
    }

    //When read a file without any given geometry dataset, it calls a routine to read geometry reserved into a HDF fild
    void bindHDF(const std::string& filename,const std::string& path = "./datasets")
    {
        std::string HDFile_name = filename+".h5";
        d_find_dataset= IsThere(filename,path);
    }
    void readFile(const std::string& filename, const std::string& source_path, const std::string& hdf_path)
    {
        bindHDF(filename,hdf_path);
        const std::string fullPath = source_path +"/"+ filename;
        if(!d_find_dataset)
        {
            readGeometry(fullPath);
            d_find_dataset = true;
        }
    
    }
private:
    hid_t d_fileId;
    hid_t d_geomGroupId;
    hid_t d_varGroupId;
    bool d_find_dataset;
    bool IsFolderExist(const std::string& path)
    {
        DIR * dp;
        if((dp=opendir(path.c_str()))==NULL)
        {
            return false;
        }
        closedir(dp);
        return true;
    }
    bool IsFileExist(const std::string& fullPath)
    {
        return !access(fullPath.c_str(),F_OK);
    }
    bool IsThere(const std::string& filename,const std::string& path)
    {
        std::string HDFile_name = path + "/"+filename;
        std::cout<<HDFile_name<<'\n';
        bool fileExist = IsFileExist(HDFile_name);
        if(fileExist)
        {
            d_fileId = H5Fopen(HDFile_name.c_str(),H5F_ACC_RDWR,H5P_DEFAULT);
            return true;
        }
        else
        {
            bool FolderExist = IsFolderExist(path);
            mode_t mode = 0755;
            if(!FolderExist)
            {
                ::mkdir(path.c_str(),mode);
            }
            d_fileId = H5Fcreate(HDFile_name.c_str(),H5F_ACC_EXCL,H5P_DEFAULT,H5P_DEFAULT);
            return false;
        }
        
        // try
        // {
        //     hid_t file_id = H5Fopen(HDFile_name.c_str(),H5F_ACC_RDWR,H5P_DEFAULT);
        // }
        // catch(const std::exception& e)
        // {
        //     std::cerr << e.what() << '\n';
        // }
        
//        std::cout<<file_id<<'\n';

    }

};


int main()
{
    int textLines[NBLOCKS] = {16,6+1};
    int n_allNodes[NBLOCKS] = {19068,77230};
    int n_allElems[NBLOCKS] = {35748, 73500};
    int n_coord = 3;
    int n_var = 6;
    int abandoned_cor_ind = 2;
    double xmin[3] = {-5,-5,-5};
    double xmax[3] = {5,5,5};
    PackType ptp[NBLOCKS] = {PackType::FETRIANGLE,PackType::FEQUADRILATERAL};
    Tecplot_MetaData<NBLOCKS> meta(textLines,
    n_allNodes,
    n_allElems,
    n_coord,
    n_var,
    true,
    xmax,
    xmin,
    2,ptp);
    std::vector<std::string> to_read_files;
    to_read_files.push_back("theOnly.dat");
    //Here are some code to push name into vectors
    HDF_writer<NBLOCKS> writer(meta);
    writer.readFile("theOnly","./","./dataset");
    // for(int i = 0 ;i<to_read_files.size();i++)
    // {
    //     writer.readFile(to_read_files[i]);
        

    // }
    

}