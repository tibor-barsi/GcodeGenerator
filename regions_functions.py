import numpy as np

class Regions():
    def __init__(self, ref_pos=(0,0)):
        self.ref_pos = np.array(ref_pos)
        self.regions = {}
    
    def add_region(self, name, pos, dim, layer, z_height, reg_type, mat, start_pos, infill_angle, perimeter, 
                   overlap_factor=0.25, speed_factor=1.0, extrude_factor=1.0):
        """Adds region to the regions dictionary.

        TODO:
        - dodaj možnost, da se regija definira glede na obstoječo regijo z offsetom.
        
        Parameters
        ----------
        name : str
            Name of the region.
        pos : list
            Position of the region. If the position is defined in relation to existing region, the first element of the list is the name of the existing region.
        dim : list
            Dimensions of the region. If the dimensions are defined in relation to existing region, the first element of the list is the name of the existing region.
        layer : int
            Layer number of the region.
        z_height : float
            Z height of the region (nozzle position). If z_height==None, the z_height is calculated from the layer number and layer_height from print_params.
        reg_type : str
            Type of the region. Can be 'infill', 'perimeter'.
        mat : str
            Material of the region.
        start_pos : str
            Starting position of the region. Can be ['x0', 'y0'], ['x0', 'y1'], ['x1', 'y0'], ['x1', 'y1'].
        infill_angle : float
            Angle of the infill. Can be 0, 90.
        perimeter : int
            Number of perimeters.
        overlap_factor : float, optional
            Overlap factor of the infill/perimeter. The default is 0.25.
        speed_factor : float, optional
            Printing speed factor of the region. The default is 1.0.
        extrude_factor : float, optional
            Extrusion factor of the region. The default is 1.0.

        Returns
        -------
        None.

        Examples
        --------
        >>> regions = Regions()
        # TODO

        """
        # dim
        if len(dim) == 2:
            dim = np.array(dim)
            
        elif len(dim) == 3 and dim[0] in self.regions.keys():
            rel_reg = self.regions[dim[0]] # relation region
            rel_reg_dim = rel_reg['dimensions']
            
            dim = np.array(dim[1:])
            dim = rel_reg_dim + dim
            
        else:
            raise Exception('Zajebuu pri dimensions')
            
            
        # pos
        if len(pos) == 2: # position is explicitly defined
            pos = self.ref_pos + np.array(pos)
            
        elif len(pos) == 3 and pos[0] in self.regions.keys(): # position is defined in relation to existing region
            rel_reg = self.regions[pos[0]] # relation region
            rel_reg_pos = rel_reg['position']
            rel_reg_dim = rel_reg['dimensions']
            
            pos_temp = np.array([0.,0.])
            if isinstance(pos[1], str): # relation in x-axis
                if pos[1] == 'right':
                    pos_temp[0] = rel_reg_pos[0] + rel_reg_dim[0]
                elif pos[1] == 'left':
                    pos_temp[0] = rel_reg_pos[0] - dim[0]
            else:
                pos_temp[0] = rel_reg_pos[0] + pos[1]
                    
            if isinstance(pos[2], str): # relation in y-axis
                if pos[2] == 'top':
                    pos_temp[1] = rel_reg_pos[1] + rel_reg_dim[1]
                elif pos[2] == 'bottom':
                    pos_temp[1] = rel_reg_pos[1] - dim[1]
            else:
                pos_temp[1] = rel_reg_pos[1] + pos[2]
                
            pos = pos_temp
            
        else:
            raise Exception('Zajebuu pri position')
            
        self.regions[name] = {
            'position': pos,
            'dimensions': dim,
            'layer':layer, 
            'z_height': z_height,
            'region_type':reg_type, 
            'material':mat, 
            'start_pos':start_pos, 
            'infill_angle':infill_angle, 
            'perimeter':perimeter,  
            'overlap_factor':overlap_factor, 
            'speed_factor':speed_factor, 
            'extrude_factor':extrude_factor,
            'heading': name
        }
