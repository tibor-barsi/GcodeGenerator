import json
import numpy as np

def save_params(params_dict, filepath):
    """Saves parameters in a .json file.

    Args:
        params_dict (dict): Printing params.
        filepath (string): Must include .json.
    """
    with open(filepath, 'w') as f:
        f.write(json.dumps(params_dict, indent=True))
        
def load_params(filepath):
    """Loads parameters from .json file to dict.

    Args:
        filepath (string): path to .json file

    Returns:
        dict: parameters
    """
    with open(filepath) as f:
        params_dict = json.loads(f.read())
    return params_dict

def printer_start(printer_settings):
    """
    Generates start g-code.
    Params:
    tools       ... list of needed tool names: ['T1', 'T2', ...]
    temps       ... dict of temps for every tool and bed: {'T1': [nozzle_temp, idle_temp], 'bed': 60, ...}
    mesh_bed    ... dict of locations and number of points {'X': [xmin, xmax], ..., 'P': 3}
    """
    
    g_code = '; --- Printer start g-code - start\n'
    
    #g_code += 'M42 P7 S255 ; lights on\n'
    #g_code += 'M42 P100 S1 ; stepper fans on\n\n'
    
    tools_dict = printer_settings['tools']
    temps_dict = printer_settings['temps']
    
    # activating tools
    for tool_key in tools_dict.values():
        g_code += f'{tool_key} P0 ; activating tool {tool_key}\n'
    g_code += f'T-1 P0 ; clear tool selection\n'
    g_code += '\n'
        
    # setting temps
    for material, tool_key in tools_dict.items():
        tool_num = int(tool_key[-1])
        temp1, temp2 = temps_dict[material]
        g_code += f'G10 P{tool_num} S{temp1} ; set tool {tool_num} extruder temp\n'
        g_code += f'G10 P{tool_num} R{temp2} ; set tool {tool_num} idle temp\n'
    #all_temps = [temp for tool_temps in temps.values() for temp in tool_temps]
    g_code += f'M302 S120 ; set cold extrusion limit\n'
    
    # print bed temp
    bed_temp = temps_dict['bed']
    g_code += f'M140 S{bed_temp} ; set bed temp\n'
    g_code += f'M190 S{bed_temp} ; wait for bed temp\n'
    g_code += '\n'
    
    if printer_settings['mesh_bed'] == None:
        mesh_bed = {
            'X': [100, 200],
            'Y': [50, 150],
            'P': 3
        }
    else:
        mesh_bed = printer_settings['mesh_bed']
    
    # homing and mesh bed leveling
    g_code += 'T-1 ; clear tool selection\n'
    g_code += f'G28 ; home all\n'
    x_mesh = mesh_bed['X']
    y_mesh = mesh_bed['Y']
    p_mesh = mesh_bed['P']
    g_code += f'M557 X{x_mesh[0]}:{x_mesh[1]} Y{y_mesh[0]}:{y_mesh[1]} P{p_mesh} ; mesh bed leveling\n'
    g_code += 'G29 ; probe the bed, save the height map, and activate bed compensation\n'
    
    # other
    g_code += 'G21 ; set units to millimeters\n'
    g_code += 'G90 ; use absolute coordinates\n'
    g_code += 'M83 ; use relative distances for extrusion\n'
    g_code += 'T-1 ; clear tool selection\n'
    
    g_code += '; --- Printer start g-code - end\n\n'
    
    return g_code


def load_tool(material, printer_settings, tool_fans=None):
    """
    Generates g-code for first tool load.
    Params:
    tool ... tool name: 'T0'
    cooling ... dict: {'T1': 0.0 ... 1.0, ...}
    prime_macro ... dict: {'T1': 'macro_name', ...}
    
    TODO: K_factor
    """
    
    if tool_fans == None:
        # specifing fan pins for each extruder
        tool_fans = {
            'T0': 'P2',
            'T1': 'P4',
            'T2': 'P6',
            'T3': 'P8',
            'T4': 'P0'
        }
    
    tool = printer_settings['tools'][material]    
    fan = tool_fans[tool]
    cooling = printer_settings['cooling'][material]
    prime_macro = printer_settings['prime_macro'][material]
    
    g_code = f'; --- Tool load: {str(tool)} : {material} - start\n'
    g_code += 'T-1 ; clear tool selection\n'
    g_code += f'{tool} ; load tool\n'
    g_code += f'M116 P{tool[-1]} ; wait for extruder to reach temp.\n'
    g_code += f'M106 {fan} S{cooling} ; turn on PCF for mounted tool\n'
    g_code += f'M98 P"{prime_macro}.g" ; prime extruder\n'
    g_code += f'; --- Tool load: {str(tool)} - end\n\n'
    
    return g_code
    

def unload_tool(material, printer_settings, tool_fans=None):

    if tool_fans == None:
        # specifing fan pins for each extruder
        tool_fans = {
            'T0': 'P2',
            'T1': 'P4',
            'T2': 'P6',
            'T3': 'P8',
            'T4': 'P0'
        }
        
    tool = printer_settings['tools'][material]
    fan = tool_fans[tool]

    g_code = f'; --- Tool unload: {str(tool)} - start\n'
    g_code += 'T-1 ; unload current tool\n'
    g_code += f'M106 {fan} S0 ; turn off PCF for dismounted tool\n'
    g_code += f'; --- Tool unload: {str(tool)} - end\n\n'
    
    return g_code
    

def tool_change(current_material, next_material, printer_settings, tool_fans=None, beep=True):
    """
    Generates g-code for first tool load.
    Params:
    tool ... tool name: 'T0'
    cooling ... dict: {'T1': 0.0 ... 1.0, ...}
    prime_macro ... dict: {'T1': 'macro_name', ...}
    """
    
    if tool_fans == None:
        # specifing fan pins for each extruder
        tool_fans = {
            'T0': 'P2',
            'T1': 'P4',
            'T2': 'P6',
            'T3': 'P8',
            'T4': 'P0'
        }
    
    current_tool = printer_settings['tools'][current_material]
    next_tool = printer_settings['tools'][next_material]
    
    current_fan = tool_fans[current_tool]
    next_fan = tool_fans[next_tool]
    cooling = printer_settings['cooling'][next_material]
    prime_macro = printer_settings['prime_macro'][next_material]
    
    tool_string = f'{str(current_tool)} -> {str(next_tool)}'
    mat_string = f'{str(current_material)} -> {str(next_material)}'
    g_code = f'; --- Tool change: {tool_string} : {mat_string} - start\n'
    if beep:
        g_code += play_sound(intensity=1)
    g_code += 'T-1 ; unload current tool\n'
    g_code += f'M106 {current_fan} S0 ; turn off fan for current tool\n'
    g_code += f'{next_tool} ; load next tool\n'
    g_code += f'M116 P{next_tool[-1]} ; wait for extruder to reach temp.\n'
    g_code += f'M106 {next_fan} S{cooling} ; turn on PCF for mounted tool\n'
    g_code += f'M98 P"{prime_macro}.g" ; prime extruder\n'
    g_code += f'; --- Tool change: {tool_string} : {mat_string} - end\n\n'
    
    return g_code


def take_photo(current_tool, next_tool, printer_settings, tool_fans=None, beep=True):
    """
    Functions generated g-code which:
    1) unloads current tool,
    2) pauses print and sets pin for layer cam script,
    3) loads tool.
    
    Args:
        current_tool (string): current loaded tool (to know which fan to disable)
        next_tool (string): tool needed after layer cam
        cooling (dict): cooling fans for each tool
        prime_macro (dict): prime macros for each tool
        K_factor (dict, optional): K-factor for each tool. Defaults to None.
        tool_fans (dict, optional): cooling fan pin for each tool. Defaults to None.
        beep (bool, optional): makes beep. Defaults to True.

    Returns:
        g_code [string]: g_code for layer cam
    """
    g_code = '; photo - start\n'
    if beep:
        g_code += play_sound(intensity=2)
    # unload tool
    if current_tool != None:
        g_code += unload_tool(current_tool, printer_settings, tool_fans=tool_fans)
    # take photo
    g_code += 'M400\nM42 P102 S1\nM226\n'
    # load next tool
    if next_tool != None:
        g_code += load_tool(next_tool, printer_settings, tool_fans=tool_fans)
    g_code += '; photo - end\n\n'
    
    return g_code

def play_sound(intensity=1):
    if intensity == 1:
        g_code = [
            '; play sound\n',
            'M300 S1000 P1000\n',
            'G4 P500\n',
            'M300 S1000 P1000\n'
        ]
    elif intensity == 2:
        g_code = [
            '; play sound\n',
            'M300 S1200 P1000\n',
            'G4 P500\n',
            'M300 S1200 P1000\n',
            'G4 P500\n',
            'M300 S1200 P1000\n',
            'G4 P500\n',
            'M300 S1200 P1000\n'
        ]
    elif intensity == 3:
        g_code = [
            '; play sound\n',
            'M300 S1700 P1000\n',
            'G4 P300\n',
            'M300 S1700 P1000\n',
            'G4 P300\n',
            'M300 S1700 P1000\n',
            'G4 P300\n',
            'M300 S1700 P1000\n',
            'G4 P300\n',
            'M300 S1700 P1000\n',
            'G4 P300\n',
            'M300 S1700 P1000\n',
            'G4 P300\n',
            'M300 S1700 P1000\n',
            'G4 P300\n',
            'M300 S1700 P1000\n'
        ]        
    return ''.join(g_code)

def printer_stop():
    g_code = [
        '; printer stop\n',
        'G91 ; use relative positioning\n',
        'G1 Z10 F1000 ; drop Bed 10mm\n',
        'G90 ; use absolute positioning\n',
        'T-1 ; unload tool\n',
        'M106 P8 S0 ; turn off PCF for mounted tool\n',
        'G29 S2 ; disable mesh compensation.\n',
        'G1 X-30 Y180 F10000 ; park gantry at back-left of machine\n',
        #'M42 P7 S0 ; lights off\n',
        #'M42 P100 S0 ; stepper fans off\n',
        'M0 ; stop all\n',
        play_sound(intensity=3)
    ]
    return ''.join(g_code)