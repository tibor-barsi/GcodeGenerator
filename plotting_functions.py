import numpy as np
from gcode_functions import get_print_limits


def plot_defined_regions(fig, ax, regions, layer, trace_width=0.42, colors=None, **kwargs):
    """Plots regions on a 3D printer's build plate.

    Args:
        fig (obj): matplotlib figure object
        ax (obj): matplotlib ax object
        regions (dict): dict of regions with region specs
        layer (int, list, tuple): layer to plot, all regions in a specified layer will be plotted

    Example of regions dict:
        regions = {
        'Eel': {
            'layer': 1,
            'region_type': 'surface',
            'material': 'electrode',
            'position': [155, 155],
            'dimensions': [20, 20],
            'start_pos': ['x1', 'y1'],
            'speed_factor': 1.0,
            'extrude_factor': 1.0,
            'heading': 'Eel surface'        
        }}
    """

    from matplotlib.patches import Polygon
    import matplotlib.colors as mcolors
    
    # defining color for each region
    if colors == None:
        reg_colors = {}
        all_colors = list(mcolors.TABLEAU_COLORS.keys())
        for i, region in enumerate(regions.keys()):
            reg_colors[region] = all_colors[i]
    else:
        reg_colors = {}
        for key, color in colors.items():
            for reg_key, reg in regions.items():
                if key in reg['material']:
                    reg_colors[reg_key] = color
                    
    
    def get_points_for_Polygon(pos, dims):
        """Returns points from the position and dimension information 
        for the Plygon matplotlib object.

        Args:
            pos (list): 2-list
            dims (list): 2-list

        Returns:
            numpy array: points for Polygon object
        """
        pos = np.asarray(pos)
        dims = np.asarray(dims)
        points = np.asarray([
            pos, # lower left vertice
            [pos[0] + dims[0], pos[1]], # lower right vertice
            pos + dims, # upper right vertice
            [pos[0], pos[1] + dims[1]]]) # upper left vertice
        return points
    
    def plot_surface(pos, dims, **kwargs):
        points = get_points_for_Polygon(pos, dims)
        rectangle = Polygon(points, **kwargs)
        ax.add_patch(rectangle)
    
    def plot_perimeter(pos, dims, label=None, **kwargs):
        w = trace_width
        points = get_points_for_Polygon(pos, dims) # rectange vertices
        ll, lr, ur, ul = points
        rectangle = Polygon(points + np.array([[1, 1], [-1,1], [-1,-1], [1,-1]]) * w/2, fill=False, color='k', linestyle='--')
        rectangle_left = Polygon([ll, ul, ul + np.array([w, 0]), ll + np.array([w, 0])], label=label, **kwargs)
        rectangle_right = Polygon([lr - np.array([w, 0]), ur - np.array([w, 0]), ur, lr], **kwargs)
        rectangle_top = Polygon([ul - np.array([0,w]), ul, ur, ur - np.array([0, w])], **kwargs)
        rectangle_bottom = Polygon([ll, ll + np.array([0, w]), lr + np.array([0, w]), lr], **kwargs)
        ax.add_patch(rectangle_left)
        ax.add_patch(rectangle_right)
        ax.add_patch(rectangle_top)
        ax.add_patch(rectangle_bottom)
        ax.add_patch(rectangle)
    
    def get_start_position(pos, dims, start_pos):
        x_int = int(start_pos[0][1])
        y_int = int(start_pos[1][1])
        x = [pos[0], pos[0] + dims[0]][x_int]
        y = [pos[1], pos[1] + dims[1]][y_int]
        return x, y
    
    def plot_start_position(pos, dims, start_pos, **kwargs):
        """Plots an X at the printing start position of a region.

        Args:
            pos (list): 2-list
            dims (list): 2-list
            start_pos (list): 2-list of strings, (x0, y0) or (x1, y0) ...
        """
        x, y = get_start_position(pos, dims, start_pos)
        ax.plot(x, y, 'x', **kwargs)
    
    def plot_infill_direction(pos, dims, start_pos, infill_angle, **kwargs):
        """Plots an arrow pointing in direction of infill.

        Args:
            pos (list): 2-list
            dims (list): 2-list
            start_pos (list): 2-list of strings, (x0, y0) or (x1, y0) ...
            infill_angle (int): 0° or 90°
        """
        x, y = get_start_position(pos, dims, start_pos)
        if infill_angle == 0:
            if start_pos[0] == 'x0':
                dx = 0.5 * dims[0]
            elif start_pos[0] == 'x1':
                dx = -0.5 * dims[0]
            dy = 0
        elif infill_angle == 90:
            dx = 0
            if start_pos[1] == 'y0':
                dy = 0.5 * dims[1]
            elif start_pos[1] == 'y1':
                dy = -0.5 * dims[1]
        ax.arrow(x, y, dx, dy, **kwargs)
        
    # condition for layer plotting
    def get_layer_condition(region_layer):
        """Determines which regions to plot besed on the specified 
        layer and region layer.

        Args:
            region_layer (int): layer of the region

        Returns:
            bool: True for plot, False for no plot
        """
        if isinstance(layer, int):
            condition = region_layer == layer
        elif isinstance(layer, list) or isinstance(layer, tuple):
            condition = region_layer in layer
        return condition
    
    w = trace_width
    for region, reg_specs in regions.items():
        if get_layer_condition(reg_specs['layer']):
            pos = reg_specs['position']
            dims = reg_specs['dimensions']
            label = reg_specs['heading']
            try:
                c = reg_colors[region]
            except Exception:
                print(Exception)
            # plotting surface
            if reg_specs['region_type'] == 'surface':
                if reg_specs['perimeter']:
                    plot_perimeter(pos, dims, color=c, **kwargs)
                    pos2 = pos + np.array([w, w])
                    dims2 = dims - np.array([2*w, 2*w])
                    plot_surface(pos2, dims2, label=label, color=c, **kwargs)
                else:
                    plot_surface(pos, dims, label=label, color=c, **kwargs)
            # plotting perimeter
            elif reg_specs['region_type'] == 'perimeter':
                plot_perimeter(pos, dims, label=label, color=c, **kwargs)
            # plotting start position
            start_pos = reg_specs['start_pos']
            plot_start_position(pos, dims, start_pos, color='k',
                                lw=2*0.3, **kwargs)
            # plotting infill direction
            infill_angle = reg_specs['infill_angle']
            plot_infill_direction(pos, dims, start_pos, infill_angle, 
                                  width=0.3, facecolor=c, **kwargs)#, head_width=10)
    if isinstance(layer, int):
        ax.legend(loc=(1.1, 0))
    ax.set_title(f'Layers: {layer}')
    
    print_limits = get_print_limits(regions)
    
    # setting ax limits
    for i in range(2):
        for j in range(2):
            ax.set_aspect('equal')
            ax.set_xlim(0.98 * print_limits['x_min'], 1.02 * print_limits['x_max'])
            ax.set_ylim(0.98 * print_limits['y_min'], 1.02 * print_limits['y_max'])