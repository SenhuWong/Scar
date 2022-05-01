import struct
from enum import Enum
plt_filename = 'unrans-3990.plt'
plt_title = 'Tecplot Export'
plt_variables = ['CoordinateX',
                 'CoordinateY',
                 'CoordinateZ',
                 'mean-pressure-coefficient',
                 'X Component Velocity',
                 'Pressure',
                 'Y Component Velocity',
                 'mean-x-velocity',
                 'mean-y-velocity',]
plt_zones = ['plane-0 Step 1 Incr 0',]
print(len(plt_title))
print(len(plt_variables[0]))

print('p',struct.calcsize("p"))
class ZoneType(Enum):
    NoneType = -1
    Ordered = 0
    FELineSeg = 1
    FETriangle = 2
    FEQuadrilateral = 3
    FETetrahedron = 4
    FEBrick = 5
    FEPolygon = 6
    FEPolyhedron = 7
# ZoneType = Enum(ORDERED=0,FELINESEG=1,FETRIANGLE=2,FEQUADRILATERAL=3,FETETRAHEDRON=4,FEBRICK=5,FEPOLYGON=6,FEPOLYHEDRON=7)
class TecplotReader:
    def __init__(self):
        self.readBinary:bool = False
        self.dataPacking:int = -1
        self.specify_var_location:int = -1
        self.zone_type:ZoneType = ZoneType.NoneType
        self.variable_locations = None
        return

    def read_bin(self):
        self.readBinary = True

    def read_asc(self):
        self.readBinary = False

    def parse_file(self, file_name, title, variables, zones):
        if self.readBinary:
            self.parse_binary(file_name,title,variables, zones)
        else:
            self.parse_ascii(file_name,title,variables, zones)

    def parse_ascii(self, filename, title, variables):
        return

    def parse_binary(self, filename, title, variables, zones):
        INT_BYTES = 4
        FLOAT_BYTES = 4
        DOUBLE_BYTES = 8
        with open(filename,"rb") as f:
            # Read first 8 bytes as magic number
            data = f.read(2*INT_BYTES)
            print(data)
            # Read an integer of value 1
            data = f.read(INT_BYTES)
            print(struct.unpack("i",data)[0])
            # Read fileType
            data = f.read(INT_BYTES)
            print(struct.unpack("i",data)[0])
            # Read Title
            read_title = f.read(INT_BYTES*(len(title)+1))
            print(read_title.decode(encoding='utf-8'))
            # read_title = struct.unpack("{}p".format(len(title)), read_title)[0]
            print(struct.unpack("i",f.read(INT_BYTES)))

            for var in variables:
                var_read = f.read(INT_BYTES*(len(var)+1))
                print(var_read.decode(encoding='utf-8'))
            # iv.Zones
            zone_marker = f.read(FLOAT_BYTES)
            print('zone_marker',struct.unpack("f",zone_marker))
            for zone in zones:
                zone_read = f.read(INT_BYTES*(len(zone)+1))
                print(zone_read.decode(encoding='utf-8'))
            # Parent Zone is -1(in this case)
            print('Parent Zone:',struct.unpack("i",f.read(INT_BYTES)))
            # Strand ID: -2 = pending strand ID for assignment by tecplot
            #            -1 = static strand ID
            #            0 <= N < 32700 valid strand ID
            print('Strand ID:',struct.unpack("i", f.read(INT_BYTES)))
            # Solution time is a double
            print("Solution time:",struct.unpack("d", f.read(DOUBLE_BYTES)))
            # Unused -1.
            print(struct.unpack("i", f.read(INT_BYTES)))
            # ZoneType 0=ORDERED, 1=FELINESEG, 2=FETRIANGLE, 3=FEQUADRILATERAL,
            #          4=FETETRAHEDRON 5=FEBRICK 6=FEPOLYGON 7=FEPOLYHEDRON
            self.zone_type = ZoneType(struct.unpack("i", f.read(INT_BYTES))[0])
            print("Zone type:",self.zone_type)
            # Data Packing 0 = Block 1 = Point
            self.dataPacking = struct.unpack("i", f.read(INT_BYTES))[0]
            print("Data Packing:",self.dataPacking)

            # Specify Var location or not.
            # 0 = All at node, no specify
            # 1 = Specify
            self.specify_var_location = struct.unpack("i", f.read(INT_BYTES))[0]
            print("Specify var location:",self.specify_var_location)
            if self.specify_var_location == 1:
                self.dataPacking = []
                for var in variables:
                    self.dataPacking.append(struct.unpack("i", f.read(INT_BYTES))[0])
                print(self.dataPacking)

            print(struct.unpack("i", f.read(INT_BYTES)))
            user_defined_face = struct.unpack("i", f.read(INT_BYTES))[0]
            print("user_defined_face",user_defined_face)
            if(user_defined_face>0):
                print("Un defined circumenstance happened")
                return
            auxiliary_used = struct.unpack("i", f.read(INT_BYTES))[0]
            print("auxiliary_used",auxiliary_used)
            if(auxiliary_used==1):
                print("Un defined circumenstace happened")
                return
            # Geometries
            print(struct.unpack("f", f.read(INT_BYTES))[0])
            print(struct.unpack("f", f.read(INT_BYTES))[0])
            print(struct.unpack("f", f.read(INT_BYTES))[0])
            print(struct.unpack("f", f.read(INT_BYTES))[0])
            print(struct.unpack("f", f.read(INT_BYTES))[0])
            print(struct.unpack("f", f.read(INT_BYTES))[0])
            print(struct.unpack("f", f.read(INT_BYTES))[0])
            print(struct.unpack("i", f.read(INT_BYTES))[0])
            print(struct.unpack("i", f.read(INT_BYTES))[0])
            print(struct.unpack("f", f.read(INT_BYTES))[0])
            print(struct.unpack("f", f.read(INT_BYTES))[0])
            print(struct.unpack("f", f.read(INT_BYTES))[0])
            #Auxiliary
            print(struct.unpack("i", f.read(INT_BYTES))[0])

            return

            print(struct.unpack("i", f.read(INT_BYTES)))
            print(struct.unpack("i", f.read(INT_BYTES)))
            print(struct.unpack("i", f.read(INT_BYTES)))
            print(struct.unpack("i", f.read(INT_BYTES)))
            print(struct.unpack("i", f.read(INT_BYTES)))
            print(struct.unpack("i", f.read(INT_BYTES)))
            print(struct.unpack("i", f.read(INT_BYTES)))
            print(struct.unpack("i", f.read(INT_BYTES)))
            print('----------------')
            print(struct.unpack("i", f.read(INT_BYTES)))
            print(struct.unpack("i", f.read(INT_BYTES)))




            print(struct.unpack("i", f.read(INT_BYTES)))
            print(struct.unpack("i", f.read(INT_BYTES)))
            print(struct.unpack("i", f.read(INT_BYTES)))
            print(struct.unpack("i", f.read(INT_BYTES)))
            return
            #Auxihilary
            while(abs(struct.unpack("f", f.read(INT_BYTES))[0]-399.0)>1.0e-8):
                print('Not found yet')
            print('found')
            print(struct.unpack("i", f.read(INT_BYTES)))
            print(struct.unpack("i", f.read(INT_BYTES)))
            print(struct.unpack("i", f.read(INT_BYTES)))
            print(struct.unpack("i", f.read(INT_BYTES)))
            print(struct.unpack("i", f.read(INT_BYTES)))
            print(struct.unpack("i", f.read(INT_BYTES)))
            print(struct.unpack("i", f.read(INT_BYTES)))





            if self.specify_var_location == 1:
                self.dataPacking = []
                for var in variables:
                    self.dataPacking.append(struct.unpack("i",f.read(INT_BYTES))[0])
                print(self.dataPacking)
            # Are raw local 1-to-1 face neighbors supplied( 0=FALSE, 1=TRUE)
            print("Local 1-to-1 supplied?:",struct.unpack("i", f.read(INT_BYTES))[0])
            # Number of miscellaneous user-defined face neighbour connections(value>=0)

            nMiscellanrous=struct.unpack("i", f.read(INT_BYTES))[0]
            print("Number of Miscellaneous user_define face neighbor conncetion:",nMiscellanrous)
            if nMiscellanrous>0:
                print("Undefined when user-defined face neighbor connection")
            #     Do nothing now, cuz I don't need it now
            if self.zone_type==ZoneType.Ordered:
                imax,jmax,kmax = struct.unpack("{}i".format(3), f.read(3*INT_BYTES))
            elif self.zone_type==ZoneType.NoneType:
                print("Error unspecified Zone Type")
            else:
                num_pts = struct.unpack("i", f.read(INT_BYTES))[0]
                print("num_pts:",num_pts)
                if self.zone_type==ZoneType.FEPolygon or self.zone_type==ZoneType.FEPolyhedron :
                    num_fcs = struct.unpack("i", f.read(INT_BYTES))[0]
                    num_fc_nds = struct.unpack("i", f.read(INT_BYTES))[0]
                    num_bd_fcs = struct.unpack("i", f.read(INT_BYTES))[0]
                    num_bd_cns = struct.unpack("i", f.read(INT_BYTES))[0]
                num_elms,icell_dim,jcell_dim,kcell_dim = struct.unpack("{}i".format(4), f.read(INT_BYTES*4))
                print(num_elms)
                print(icell_dim)
                print(jcell_dim)
                print(kcell_dim)
                # icell_dim = struct.unpack("i", f.read(INT_BYTES))[0]
                # jcell_dim = struct.unpack("i", f.read(INT_BYTES))[0]
                # kcell_dim = struct.unpack("i", f.read(INT_BYTES))[0]

            #For all zone types:Auxiliary
            auxiliary_used = struct.unpack("i", f.read(INT_BYTES))[0]
            if auxiliary_used:
                print("Auxiliary used but I haven't provided code for it")
            print(struct.unpack("f", f.read(FLOAT_BYTES))[0])
            print(struct.unpack("f", f.read(FLOAT_BYTES))[0])
            print(struct.unpack("f", f.read(FLOAT_BYTES))[0])
            print(struct.unpack("f", f.read(FLOAT_BYTES))[0])
            print(struct.unpack("f", f.read(FLOAT_BYTES))[0])
            print(struct.unpack("f", f.read(FLOAT_BYTES))[0])
            print(struct.unpack("f", f.read(FLOAT_BYTES))[0])
            print(struct.unpack("f", f.read(FLOAT_BYTES))[0])
            print(struct.unpack("f", f.read(FLOAT_BYTES))[0])
            print(struct.unpack("f", f.read(FLOAT_BYTES))[0])
            print(struct.unpack("f", f.read(FLOAT_BYTES))[0])
            print(struct.unpack("f", f.read(FLOAT_BYTES))[0])
            print(struct.unpack("f", f.read(FLOAT_BYTES))[0])
            print(struct.unpack("f", f.read(FLOAT_BYTES))[0])
            print(struct.unpack("f", f.read(FLOAT_BYTES))[0])
            print(struct.unpack("f", f.read(FLOAT_BYTES))[0])
            print(struct.unpack("f", f.read(FLOAT_BYTES))[0])
            print('-----------------------------')







        return


reader = TecplotReader()
reader.read_bin()
reader.parse_file(plt_filename,plt_title,plt_variables,plt_zones)



