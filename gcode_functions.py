import numpy as np
import traceback

def g_code_header(printing_params):
    """Generates commented g_code of printing params for each material 
    in input dict printing params.

    Args:
        printing_params (dict): Dict of dicts of printing params. 
                                Keys are different materials.

    Returns:
        string: g_code header
    """
    
    g_code = '; Printing params - start\n\n'
    for key, params_dict in printing_params.items():
        g_code += f'; Material: {key}\n'
        for param_key, param in params_dict.items():
            g_code += f'; \t{param_key:20s} = {param}\n'
        g_code += '\n'
    g_code += '; Printing params - end\n\n'
    return g_code

def get_print_limits(regions):
    """Returns the limiting coordinates of the print.

    Args:
        regions (dict): dict of all regions with specs

    Returns:
        dict: dict of x_min, x_max, y_min, y_max
    """
    # all vartices to calculate x, y limits
    all_x = []
    all_y = []
    for reg_specs in regions.values():
        pos = reg_specs['position']
        dims = reg_specs['dimensions']
        pos = np.asarray(pos)
        dims = np.asarray(dims)
        x_min = pos[0]
        x_max = pos[0] + dims[0]
        y_min = pos[1]
        y_max = pos[1] + dims[1]
        all_x.append(x_min)
        all_x.append(x_max)
        all_y.append(y_min)
        all_y.append(y_max)
    r = {
        'x_min': np.min(all_x),
        'x_max': np.max(all_x),
        'y_min': np.min(all_y),
        'y_max': np.max(all_y),
    }
    return r


def process_g_code(filepath, tool_unload_time=3, tool_load_time=20):
    """
    Args:
        filepath (string): path to g_code file .g
        tool_unload_time (int, optional): time for tool unload in sec. Defaults to 3.
        tool_load_time (int, optional): time for tool load in sec. Defaults to 20.

    Returns:
        return_dict (dict): includes keys:
                                'print_time_hours'
                                'print_time_mins'
                                'print_time_sec'
                                'all_extrusions_mm'
                                'print_duration_sec'
                                'only_extrusion_duration_sec'
                                'tool_unloads_duration'
                                'tool_loads_duration'
    """
    
    # reading g_code lines
    with open(filepath) as f:
        lines = f.readlines()
    
    coordinates = []
    extrusions = []
    feedrates = []

    num_tool_unloads = 0
    num_tool_loads = 0
    
    for l in lines: # iterating through lines
        
        try:
            
            words = l.split() # spliting lines into words
            
            if len(words) == 0: # excluding empty lines
                continue
            
            # excluding comments
            if ';' in words:
                comment_index = words.index(';')
                if comment_index == 0: # line with only comment
                    continue
                else:
                    words = words[:comment_index]

            if words[0] in ['G0', 'G1']: # iterating over moving and printing lines

                coord = [None, None, None]
                extrusion = 0
                feedrate = None
                for word in words:

                    if len(word) < 2:
                        continue

                    if word[0] == 'X':
                        x = float(word[1:])
                        coord[0] = x
                    elif word[0] == 'Y':
                        y = float(word[1:])
                        coord[1] = y
                    elif word[0] == 'Z':
                        z = float(word[1:])
                        coord[2] = z
                    elif word[0] == 'E':
                        extrusion = float(word[1:])
                    elif word[0] == 'F':
                        feedrate = float(word[1:])

                # populating nondefined coordinates with previus coordinates
                if coord[0] == None:
                    coord[0] = x
                if coord[1] == None:
                    coord[1] = y
                if coord[2] == None:
                    coord[2] = z

                coordinates.append(coord)
                extrusions.append(extrusion)
                feedrates.append(feedrate)

            if words[0][0] == 'T': # tool loads and unloads
                if words[0] == 'T-1':
                    num_tool_unloads += 1
                else:
                    num_tool_loads += 1
        
        except Exception:
            print(f'Error at line:{l}')
            traceback.print_exc()
        
    # calculating used filament length:
    all_extrusions = np.sum(extrusions)
    
    # calculating durations:
    distances = np.abs(np.diff(np.asarray(coordinates), axis=0, prepend=0)) # razlike med posameznimi koordinatami
    absolute_distances = np.sqrt(np.sum(np.square(distances), axis=1)) # sqrt(x^2 + y^2 + z^2) - dolžina vektroja pomika
    print_durations = absolute_distances / (np.asarray(feedrates) / 60)
    print_duration = np.sum(print_durations)
    
    # only extrusions:
    no_movement_args = np.argwhere(absolute_distances==0)
    only_extrusions = np.abs(np.asarray(extrusions)[no_movement_args])
    only_extrusion_feedrates = np.asarray(feedrates)[no_movement_args]
    only_extrusion_durations = only_extrusions / (only_extrusion_feedrates / 60)
    only_extrusion_duration = np.sum(only_extrusion_durations)
    
    # tool changes:
    tool_unloads_duration = num_tool_unloads * tool_unload_time
    tool_loads_duration = num_tool_loads * tool_load_time
    
    # print time:
    print_time = print_duration + only_extrusion_duration + tool_unloads_duration + tool_loads_duration
    print_time_mins = print_time / 60
    print_time_hours = print_time_mins / 60
    
    return_dict = {
        'print_time_hours': round(print_time_hours, 2),
        'print_time_mins': round(print_time_mins, 2),
        'print_time_sec': round(print_time, 2),
        'all_extrusions_mm': round(all_extrusions, 2),
        'print_duration_sec': round(print_duration, 2),
        'only_extrusion_duration_sec': round(only_extrusion_duration, 2),
        'tool_unloads_duration': round(tool_unloads_duration, 2),
        'tool_loads_duration': round(tool_loads_duration, 2)
    }
    
    return return_dict




def move_g_code(g_code, dX=0, dY=0, dZ=0):
    """
    Moves g-code for specified dx, dy, dz in mm.
    Works with G0 and G1 commands.
    input:
        g_code      ... g_code in string format with \n line split
        dx, dy, dz  ... [mm]
    """

    g_code = g_code.split('\n') # spliting g_code string into lines
    
    moved_g_code = []
    for line_number, line in enumerate(g_code):
        
        words = line.split() # spliting line into words
        
        if len(words) == 0: # empty line
            moved_g_code.append(line + '\n')
            continue
            
        if line[0] == ';': # line is a comment
            moved_g_code.append(line + '\n')
            continue
        
        if words[0] == 'G0' or words[0] == 'G1':
            
            X_found, Y_found, Z_found = False, False, False
            
            new_line = [words[0]]
            
            for word in words[1:]:
                try:
                    if word[0] == 'X' and X_found == False \
                        and Y_found == False and Z_found == False:
                        X_found = True
                        
                        old_X = float(word[1:])
                        new_X = old_X + dX

                        new_word = 'X' + str(new_X)
                        new_line.append(new_word)

                    elif word[0] == 'Y' and Y_found == False \
                        and Z_found == False:
                        Y_found = True

                        old_Y = float(word[1:])
                        new_Y = old_Y + dY

                        new_word = 'Y' + str(new_Y)
                        new_line.append(new_word)

                    elif word[0] == 'Z' and Z_found == False:
                        Z_found = True

                        old_Z = float(word[1:])
                        new_Z = old_Z + dZ

                        new_word = 'Z' + str(new_Z)
                        new_line.append(new_word)

                    else:
                        new_line.append(word)
                    
                except:
                    print(f'Error at word: {word} at line: {line_number}')
            
            new_line_string = ' '.join(new_line) + '\n'
            
            moved_g_code.append(new_line_string)
            
        else:
            moved_g_code.append(line)
            continue
    
    moved_g_code_string = ''.join(moved_g_code)

    return moved_g_code_string