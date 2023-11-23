import numpy as np

class generator_multi():
    """Creates an object with attributes being G_code_generator object, 
    defined by the mat_params_dict.
    
    Params:
    mat_params_dict [dict] - keys = materials, values = dict of print parameters
    """
    def __init__(self, mat_params_dict):
        for mat, params in mat_params_dict.items():
            self.__dict__[mat] = G_code_generator(params)

class G_code_generator:
    """
    Class for generating g-code for FDM/FFF 3D printing.
    """

    def __init__(self, printing_params):
        """
        Params:
        printing_params [dict]
            printing parameters: 
                d_nozzle, d_filament, layer_height, 
                trace_width, trace_spacing, extrude_factor, 
                move_feedrate, print_feedrate, nozzle_lift, 
                retract_len, retract_feedrate, wipe_len, 
                wipe_feedrate
        """
        
        # defining printing params:
        self.printing_params = printing_params
        self.d_nozzle = printing_params['d_nozzle']
        self.d_filament = printing_params['d_filament']
        self.layer_height = printing_params['layer_height']
        self.trace_width = printing_params['trace_width']
        self.trace_spacing = printing_params['trace_spacing']
        self.extrude_factor = printing_params['extrude_factor']
        self.move_feedrate = printing_params['move_feedrate']
        self.print_feedrate = printing_params['print_feedrate']
        self.nozzle_lift = printing_params['nozzle_lift']
        self.retract_len = printing_params['retract_len']
        self.retract_feedrate = printing_params['retract_feedrate']
        self.wipe_len = printing_params['wipe_len']
        self.wipe_feedrate = printing_params['wipe_feedrate']
        
        # feedrates: mm/s to mm/min
        self.move_feedrate = self.move_feedrate * 60
        self.print_feedrate = self.print_feedrate * 60
        self.retract_feedrate = self.retract_feedrate * 60
        self.wipe_feedrate = self.wipe_feedrate * 60
        
        # internal history
        self.nozzle_locations = []
        self.current_layer_height = None
    

    def move_to_point(self, point, z, speed_factor=1, comment=None):
        """
        Generates G0 command for nozzle movement to x, y, z point.
        Slow is 20% of move feedrate.
        Comment in string format.
        Saves location to nozzle_locations.
        Params:
        point           ... list: [x, y] in mm
        z               ... z height in mm
        speed_factor    ... float: feed_rate = speed_factor * self.move_feedrate
        comment         ... string: c_code comment at end of line
        """

        x, y = point
        self.nozzle_locations.append([x, y, z])
        self.current_z = z
        
        g_code = 'G0 '
        g_code += f'X{x:.3f} '
        g_code += f'Y{y:.3f} '
        g_code += f'Z{z:.3f} '
        g_code += f'E{0:.1f} '
        g_code += f'F{self.move_feedrate * speed_factor:.0f} '
        if comment == None:
            g_code += '; move to point\n'
        else:
            g_code += f'; {comment}\n'

        return g_code

    
    def move_to_printing_point(self, point):
        """
        Generates G0 command for nozzle movement to x, y, z point in form:
        1) move over point (Z lift)
        2) lower to Z
        """
        x, y, z = point
        self.nozzle_locations.append([x, y, z]) # adding point1 to object history
        self.current_z = z
        
        # rapid move over point
        g_code = self.move_to_point([x, y], z + self.nozzle_lift, comment='move over print point')
        # lower Z
        g_code += self.move_to_point([x, y], z, speed_factor=0.2, comment='lower Z')

        return g_code
    
    
    def retract(self):
        """
        Generates G1 command for retract.
        """
        g_code  = f'G1 '
        g_code += f'E{-self.retract_len:.5f} '
        g_code += f'F{self.retract_feedrate:.0f} '
        g_code += f'; retract\n'
        return g_code
        
        
    def unretract(self):
        """
        Generates G1 command for unretract.
        """
        g_code  = f'G1 '
        g_code += f'E{self.retract_len:.5f} '
        g_code += f'F{self.retract_feedrate:.0f} '
        g_code += f'; unretract\n'
        return g_code
        
        
    def wipe(self, angle):
        """
        Generates nozzle movement for wiping with G1 command.
        Wipes back and forth.
        Params:
        angle   ... float 0 - 360 deg (0 deg parallel with x axis)
        Returns:
        g_code  ... string (2 lines)
        """
        # last nozzle location
        x0, y0, z0 = self.nozzle_locations[-1]
        # calculation of point 1
        x1 = x0 + self.wipe_len * np.cos(angle)
        y1 = y0 + self.wipe_len * np.sin(angle)
        # wipe to point 1
        g_code  = f'G1 '
        g_code += f'X{x1:.3f} '
        g_code += f'Y{y1:.3f} '
        g_code += f'F{self.wipe_feedrate:.0f} '
        g_code += '; wipe 1\n' 
        # wipe back to point 0
        g_code += f'G1 '
        g_code += f'X{x0:.3f} '
        g_code += f'Y{y0:.3f} '
        g_code += f'F{self.wipe_feedrate:.0f} '
        g_code += '; wipe 2\n'
        return g_code

    
    def calculate_extrusion_length(self, trace_length):
        """
        Function calculates length of filament needed 
        for the printing of one trace with specified dimensions.
        Based on volumetric rate equlibrium - V_in = V_out.
        Params:
        trace_length    ... float in mm
        Returns:
        extrude_length  ... float in mm
        """
        w = self.trace_width
        h = self.layer_height
        A_in = np.pi * self.d_filament**2 / 4
        A_out = (w - h) * h + np.pi * h**2 / 4
        extrude_length = A_out / A_in * trace_length * self.extrude_factor
        return extrude_length

    def _print_line(self, point0, point1,
                    extrude_factor=1, speed_factor=1, 
                    comment=None):
        """
        Generates a g-code for a line without wipe/retraction/unretraction. 
        Enables printing in 3 axis (printing over air).

        Params:
        point0          ... list: [x, y, z] in mm
        point1          ... list: [x, y, z] in mm
        extrude_factor  ... float: extrusion multiplier
        speed_factor    ... float: feed_rate = speed_factor * self.move_feedrate
        comment         ... string: c_code comment at end of line
        """

        if comment == None:
            comment = 'single line'
        
        x0, y0, z0 = point0
        x1, y1, z1 = point1

        point0 = np.array(point0)
        point1 = np.array(point1)
        line_length = np.sqrt(np.sum((point1-point0)**2))
        extrude_length = self.calculate_extrusion_length(line_length)

        g_code = ''
        # 1) move to print point
        g_code += self.move_to_printing_point([x0, y0, z0])
        # 3) print line
        g_code += f'G1 '
        g_code += f'X{x1:.3f} '
        g_code += f'Y{y1:.3f} '
        g_code += f'Z{z1:.3f} '
        g_code += f'E{extrude_length * extrude_factor:.5f} '
        g_code += f'F{self.print_feedrate * speed_factor:.0f} '
        g_code += f'; {comment}\n'
        self.nozzle_locations.append(point1) # adding point1 to object history

        return g_code
    
    def print_line(self, point0, point1, z, 
                   extrude_factor=1, speed_factor=1, comment=None):
        """
        Generates procedure for line with G1 commands.
        1) move to print point
        2) unretract
        3) print line
        4) retract
        5) wipe
        6) lift Z
        """
        if comment == None:
            comment = 'single line'
        
        x0, y0 = point0
        x1, y1 = point1
        line_length = np.sqrt((x1 - x0)**2 + (y1 - y0)**2)
        extrude_length = self.calculate_extrusion_length(line_length)
        
        self.current_z = z
        
        g_code = ''
        # 1) move to print point
        g_code += self.move_to_printing_point([x0, y0, z])
        # 2) unretract
        g_code += self.unretract()
        # 3) print line
        g_code += f'G1 '
        g_code += f'X{x1:.3f} '
        g_code += f'Y{y1:.3f} '
        g_code += f'E{extrude_length * extrude_factor:.5f} '
        g_code += f'F{self.print_feedrate * speed_factor:.0f} '
        g_code += f'; {comment}\n'
        self.nozzle_locations.append([x1, y1, z]) # adding point1 to object history
        # 4) retract
        g_code += self.retract()
        # 5) wipe
        angle = np.arctan2(y0 - y1, x0 - x1)
        g_code += self.wipe(angle)
        # 6) lift Z
        g_code += self.move_to_point([x1, y1], z + self.nozzle_lift, 
                                     speed_factor=0.2, comment='lift Z')  
        return g_code
    
    
    def print_connected_lines(self, lines, z, 
                              speed_factor=1, extrude_factor=1, comment=None):
        """
        Generates procedure for connected lines with G1 commands.
        1) move to print point
        2) unretract
        3) print lines
        4) retract
        5) wipe
        6) lift Z
        
        Params:
        lines   ... array of lines - [[x1, y1], [x2, y2]] in mm
        z       ... z height in mm
        """
        if comment == None:
            comment = 'connected line'

        x0, y0 = lines[0,0]
        self.current_z = z

        g_code = ''
        # 1) move to start point
        g_code += self.move_to_printing_point([x0, y0, z])
        # 2) unretract
        if self.extrude_factor != 0: # in case of no extrusion, unretract is not performed
            g_code += self.unretract()
        # 3) print lines
        for line in lines:

            x1, y1 = line[1]

            l = self.calc_line_length(line[0], line[1])
            e = self.calculate_extrusion_length(l)
    
            g_code += f'G1 '
            g_code += f'X{x1:.3f} '
            g_code += f'Y{y1:.3f} '
            g_code += f'E{e * extrude_factor:.5f} '
            g_code += f'F{self.print_feedrate * speed_factor:.0f} '
            g_code += f'; {comment}\n'
            
            self.nozzle_locations.append([x1, y1, z]) # adding point1 to object history
            
        # 4) retract
        if self.extrude_factor != 0: # in case of no extrusion, retract is not performed
            g_code += self.retract()
        # 5) wipe
        if self.extrude_factor != 0: # in case of no extrusion, wipe is not performed
            wipe_point = self.nozzle_locations[-2]
            angle = np.arctan2(wipe_point[1] - y1, wipe_point[0] - x1)
            g_code += self.wipe(angle)
        # 6) lift Z
        g_code += self.move_to_point([x1, y1], z + self.nozzle_lift, 
                                     speed_factor=0.2, comment='lift Z')  

        return g_code
    
    
    def print_rectangular_perimeter(self, rectangle, z, start=['x0','y0'], 
                                    speed_factor=1, extrude_factor=1, comment=None):
        """
        Params:
        rectangle   ... [lower_left_vertice, upper_right_vertice] in [x, y] format in mm
        z           ... z height for nozzle tip
        """
        if comment == None:
            comment = 'unnamed perimeter'
        
        # points in counter-clockwise direction from bottom left
        rectangle = np.array(rectangle)
        w = self.trace_width
        x0, y0 = rectangle[0] + np.array([w/2, w/2])
        x1, y1 = rectangle[1] - np.array([w/2, w/2])

        points = np.zeros((5,2))
        # populating x and y coordinates in points
        if start == ['x0', 'y0'] or start == ('x0', 'y0'):
            points[:,0] = np.asarray([x0, x1, x1, x0, x0])
            points[:,1] = np.asarray([y0, y0, y1, y1, y0])
        elif start == ['x0', 'y1'] or start == ('x0', 'y1'):
            points[:,0] = np.asarray([x0, x0, x1, x1, x0])
            points[:,1] = np.asarray([y1, y0, y0, y1, y1])
        elif start == ['x1', 'y0'] or start == ('x1', 'y0'):
            points[:,0] = np.asarray([x1, x1, x0, x0, x1])
            points[:,1] = np.asarray([y0, y1, y1, y0, y0])
        elif start == ['x1', 'y1'] or start == ('x1', 'y1'):
            points[:,0] = np.asarray([x1, x0, x0, x1, x1])
            points[:,1] = np.asarray([y1, y1, y0, y0, y1])
        else:
            raise Exception(f'{start} is an unknown start position for \"{comment}\".')

        # creating lines
        lines = []
        N_lines = len(points) - 1
        for i in range(N_lines):
            point_pair = [points[i], points[i+1]]
            lines.append(point_pair)
        lines = np.asarray(lines)
        
        # g-code
        g_code = self.print_connected_lines(
            lines,
            z,
            speed_factor=speed_factor,
            extrude_factor=extrude_factor,
            comment=comment)

        return g_code

    
    def print_surface(self, surface, z, infill_angle=0, start=['x0', 'y0'],
                      perimeter=False, overlap_factor=0.25,
                      speed_factor=1, extrude_factor=1, comment=None,
                      return_points=False):
        """
        Generates g-code for a rectangle surface.
        Params:
        surface         ... [lower_left_vertice, upper_right_vertice] in [x, y] format in mm
        z               ... z height for nozzle tip
        infill_angle    ... 0 (x direction) or 90 (y direction) deg
        start           ... 'left' or 'right'
        perimeter       ... bool (infill surface is adjusted to accomodate perimeter)
        overlap_factor  ... overlap between perimeter and infill in factor of self.trace_width
        ...
        return_points   ... returns list: [g_code, points, lines]
        """
        
        if comment == None:
            comment = 'unnamed surface'
        
        w = self.trace_width
        s = self.trace_spacing
        # self.current_z = z
        
        # if perimeter is selected, infill surface is reduced by a trace width with defined overlap
        if perimeter:
            w = self.trace_width
            perimeter_rect = np.asarray(surface)
            perimeter_gcode = self.print_rectangular_perimeter(
                perimeter_rect, 
                z, 
                start=start,
                speed_factor=speed_factor, 
                extrude_factor=extrude_factor, 
                comment=f'{comment} - perimeter'
            )
            # defining reduced infill surface
            infill_surface = np.asarray(surface) + np.asarray([[1, 1], [-1, -1]]) * w * (1 - overlap_factor)
        else:
            infill_surface = surface
        
        # defining points for infill traces/lines
        (x0, y0), (x1, y1) = infill_surface # corners of an infill surface
        lx = x1 - x0
        ly = y1 - y0
        
        if infill_angle == 0:
            dx = lx - w # diskretizacija po x osi je širina površine
            dy = s
            x_points = np.arange(x0 + w/2, x1, dx)
            y_points = np.arange(y0 + w/2, y1, dy)

            # korekcija za y točk:
            # vse točke so premaknjene, tako da 
            # sredina definiranega pravokotnika nalega s sredino infill-a
            y_max = y_points[-1] + w/2
            y_corr = y1 - y_max
            y_points = y_points + y_corr/2

            points = np.zeros((2 * y_points.shape[0], 2)) ###!!!
            
            # populating points array with x coordinates
            if start[0] == 'x0':
                points[0::4,0] = x_points[0]
                points[3::4,0] = x_points[0]
                points[1::4,0] = x_points[1]
                points[2::4,0] = x_points[1]
            elif start[0] == 'x1':
                points[0::4,0] = x_points[1]
                points[3::4,0] = x_points[1]
                points[1::4,0] = x_points[0]
                points[2::4,0] = x_points[0]
            else:
                print(f'{start[0]} is an unknown start position.')

            # populating points array with y coordinates
            if start[1] == 'y0':
                points[0::4,1] = y_points[0::2]
                points[1::4,1] = y_points[0::2]
                points[2::4,1] = y_points[1::2]
                points[3::4,1] = y_points[1::2]
            elif start[1] == 'y1':
                points[0::4,1] = y_points[-1::-2]
                points[1::4,1] = y_points[-1::-2]
                points[2::4,1] = y_points[-2::-2]
                points[3::4,1] = y_points[-2::-2]
            else:
                print(f'{start[1]} is an unknown start position.')
                 
        elif infill_angle == 90:
            dx = s
            dy = ly - w # diskretizacija po y osi je širina površine
            x_points = np.arange(x0 + w/2, x1, dx)
            y_points = np.arange(y0 + w/2, y1, dy)

            # korekcija za x točk: 
            # vse točke so premaknjene, tako da 
            # sredina definiranega pravokotnika nalega s sredino infill-a
            x_max = x_points[-1] + w/2
            x_corr = x1 - x_max
            x_points = x_points + x_corr/2

            points = np.zeros((2 * x_points.shape[-1], 2))
            
            # populating points array with x coordinates
            if start[0] == 'x0':
                points[0::4,0] = x_points[0::2]
                points[1::4,0] = x_points[0::2]
                points[2::4,0] = x_points[1::2]
                points[3::4,0] = x_points[1::2]
            elif start[0] == 'x1':
                points[0::4,0] = x_points[-1::-2]
                points[1::4,0] = x_points[-1::-2]
                points[2::4,0] = x_points[-2::-2]
                points[3::4,0] = x_points[-2::-2]
            else:
                print(f'{start[0]} is an unknown start position.')
            
            # populating points array with y coordinates
            if start[1] == 'y0':
                points[0::4,1] = y_points[0]
                points[3::4,1] = y_points[0]
                points[1::4,1] = y_points[1]
                points[2::4,1] = y_points[1]
            elif start[1] == 'y1':
                points[0::4,1] = y_points[1]
                points[3::4,1] = y_points[1]
                points[1::4,1] = y_points[0]
                points[2::4,1] = y_points[0]
            else:
                print(f'{start[1]} is an unknown start position.')
    
        else:
            print(f'{infill_angle} infill angle unknown.')
            
        # points = np.asarray(points)
        # points = np.round(points, 5)
        
        lines = []
        N_lines = len(points) - 1
        
        for i in range(N_lines):
            point_pair = [points[i], points[i+1]]
            lines.append(point_pair)
        lines = np.asarray(lines)
        
        g_code = ''
        if perimeter:
            g_code += perimeter_gcode
        g_code += self.print_connected_lines(
            lines, 
            z, 
            speed_factor, 
            extrude_factor, 
            comment=f'{comment} - infill'
        )
        
        if return_points:
            output = [g_code, points, lines]
        else:
            output = g_code

        return output
    



    def print_region(self, region_params, **kwargs):
        """
        TODO: update docstring
        Generates g-code based on region parameters. Utilises print_surface and 
        print_rectangular_perimeter functions of the class.

        Args:
            region_params (dict): dict of regions params with keys: 
                                            layer, region_type, material,
                                            position, dimensions, start_pos,
                                            infill_angle, perimeter, overlap_factor,
                                            speed_factor, extrude_factor, heading
        
            **kwargs: overide of the the region params with kwargs
        """
        
        # overide of the the region params with kwargs
        region_params = region_params.copy()
        region_params.update(kwargs)


        pos = np.asarray(region_params['position'])
        dims = np.asarray(region_params['dimensions'])
        surface = [pos, pos + dims]
        if region_params['z_height'] is None: # checks if layer is defined as layer number or z height
            z = region_params['layer'] * self.layer_height
        else:
            z = region_params['z_height']
        start = region_params['start_pos']
        speed_factor = region_params['speed_factor']
        extrude_factor = region_params['extrude_factor']
        comment = region_params['heading']

        if region_params['region_type'] == 'surface':
            infill_angle = region_params['infill_angle']
            perimeter = region_params['perimeter']
            overlap_factor = region_params['overlap_factor']

            g_code = self.print_surface(surface=surface, z=z, infill_angle=infill_angle, 
                                        start=start, perimeter=perimeter, overlap_factor=overlap_factor,
                                        speed_factor=speed_factor, extrude_factor=extrude_factor, 
                                        comment=comment, return_points=False)
        
        elif region_params['region_type'] == 'perimeter':
            g_code = self.print_rectangular_perimeter(rectangle=surface, z=z, start=start, 
                                                      speed_factor=speed_factor, 
                                                      extrude_factor=extrude_factor, comment=comment)
        
        return g_code
    
    
    def print_cuboid(self, surface, z_start, height, skirts=None, perimeter=False,
                      speed_factor=1, extrude_factor=1, comment=None):
        """Generates g_code for a cuboid.

        Args:
            surface (list): list specifing surface vertices (bottom left, top right)
            z_start (float): start z height (nozzle location) in mm.
            height (float): height of cuboid in mm.
            skirts (list, optional): list of lists for skirts to be printed with cuboid. Defaults to None.
            perimeter (bool, optional): Defaults to False.
            speed_factor (int, optional): Defaults to 1.
            extrude_factor (int, optional): Defaults to 1.
            heading (string, optional): Defaults to None.
            
        Returns:
            g_code_dict (dict): g_code strings for each layer height.
        """
        if comment == None:
            comment = 'unnamed cuboid'
            
        num_of_layers = round(height / self.layer_height)
        start_positions = [['x0', 'y0'], ['x1', 'y1']]
        
        g_code_dict = {} # empty dict for g_code strings for each layer
        
        for i in range(num_of_layers): # iteration over layers
            z = z_start + i * self.layer_height # current layer height
            
            g_code = ''
            if i == 0: # first layer - printed slower and thicker (higher extrude rate)
                if skirts != None: # printing skirts
                    for sk_i, skirt in enumerate(skirts):
                        g_code += self.print_rectangular_perimeter(skirt, 
                                                                   z, 
                                                                   speed_factor=0.8, 
                                                                   extrude_factor=1.0, 
                                                                   comment=f'skirt_{sk_i}')

                infill_angle = (i % 2) * 90 # alternating infill
                start_pos = start_positions[(i % 2)] # alternating start position
                g_code += self.print_surface(surface, # printing surface
                                             z, 
                                             infill_angle, 
                                             start=start_pos, 
                                             perimeter=perimeter, 
                                             speed_factor=speed_factor*0.7, 
                                             extrude_factor=extrude_factor*1.05, 
                                             comment=comment)
                 
            else: # other layers
                if skirts != None: # printing skirts
                    for sk_i, skirt in enumerate(skirts):
                        g_code += self.print_rectangular_perimeter(skirt, 
                                                                   z, 
                                                                   speed_factor=0.7, 
                                                                   extrude_factor=1.2, 
                                                                   comment=f'skirt_{sk_i}')
                infill_angle = (i % 2) * 90 # alternating infill
                start_pos = start_positions[(i % 2)] # alternating start position
                g_code += self.print_surface(surface, # printing surface
                                             z, 
                                             infill_angle, 
                                             start=start_pos, 
                                             perimeter=perimeter, 
                                             comment=comment)
            
            g_code_dict[round(z, 2)] = g_code
            
        z_last = round(z, 2)
        
        return g_code_dict, z_last
    
       
    def calc_line_length(self, point0, point1):
        point0 = np.asarray(point0)
        point1 = np.asarray(point1)
        l = np.sqrt(np.sum(np.abs(point0 - point1)**2))
        return l
    