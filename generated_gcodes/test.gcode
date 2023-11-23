; --- Printer start g-code - start
T3 P0 ; activating tool T3
T1 P0 ; activating tool T1
T-1 P0 ; clear tool selection

G10 P3 S215 ; set tool 3 extruder temp
G10 P3 R200 ; set tool 3 idle temp
G10 P1 S230 ; set tool 1 extruder temp
G10 P1 R180 ; set tool 1 idle temp
M302 S120 ; set cold extrusion limit
M140 S60 ; set bed temp
M190 S60 ; wait for bed temp

T-1 ; clear tool selection
G28 ; home all
M557 X155.0:175.0 Y120.0:140.0 P5 ; mesh bed leveling
G29 ; probe the bed, save the height map, and activate bed compensation
G21 ; set units to millimeters
G90 ; use absolute coordinates
M83 ; use relative distances for extrusion
T-1 ; clear tool selection
; --- Printer start g-code - end

; --- Tool load: T3 : PLA - start
T-1 ; clear tool selection
T3 ; load tool
M116 P3 ; wait for extruder to reach temp.
M106 P8 S1 ; turn on PCF for mounted tool
M98 P"prime.g" ; prime extruder
; --- Tool load: T3 - end

; print surface - conductive - start
G0 X174.790 Y139.790 Z0.400 E0.0 F30000 ; move over print point
G0 X174.790 Y139.790 Z0.200 E0.0 F6000 ; lower Z
G1 E0.80000 F1200 ; unretract
G1 X155.210 Y139.790 E0.58322 F2400 ; PLA surface - perimeter
G1 X155.210 Y120.210 E0.58322 F2400 ; PLA surface - perimeter
G1 X174.790 Y120.210 E0.58322 F2400 ; PLA surface - perimeter
G1 X174.790 Y139.790 E0.58322 F2400 ; PLA surface - perimeter
G1 E-0.80000 F1200 ; retract
G1 X174.790 Y138.290 F1200 ; wipe 1
G1 X174.790 Y139.790 F1200 ; wipe 2
G0 X174.790 Y139.790 Z0.400 E0.0 F6000 ; lift Z
G0 X174.475 Y139.400 Z0.400 E0.0 F30000 ; move over print point
G0 X174.475 Y139.400 Z0.200 E0.0 F6000 ; lower Z
G1 E0.80000 F1200 ; unretract
G1 X155.525 Y139.400 E0.56446 F2400 ; PLA surface - infill
G1 X155.525 Y139.000 E0.01191 F2400 ; PLA surface - infill
G1 X174.475 Y139.000 E0.56446 F2400 ; PLA surface - infill
G1 X174.475 Y138.600 E0.01191 F2400 ; PLA surface - infill
G1 X155.525 Y138.600 E0.56446 F2400 ; PLA surface - infill
G1 X155.525 Y138.200 E0.01191 F2400 ; PLA surface - infill
G1 X174.475 Y138.200 E0.56446 F2400 ; PLA surface - infill
G1 X174.475 Y137.800 E0.01191 F2400 ; PLA surface - infill
G1 X155.525 Y137.800 E0.56446 F2400 ; PLA surface - infill
G1 X155.525 Y137.400 E0.01191 F2400 ; PLA surface - infill
G1 X174.475 Y137.400 E0.56446 F2400 ; PLA surface - infill
G1 X174.475 Y137.000 E0.01191 F2400 ; PLA surface - infill
G1 X155.525 Y137.000 E0.56446 F2400 ; PLA surface - infill
G1 X155.525 Y136.600 E0.01191 F2400 ; PLA surface - infill
G1 X174.475 Y136.600 E0.56446 F2400 ; PLA surface - infill
G1 X174.475 Y136.200 E0.01191 F2400 ; PLA surface - infill
G1 X155.525 Y136.200 E0.56446 F2400 ; PLA surface - infill
G1 X155.525 Y135.800 E0.01191 F2400 ; PLA surface - infill
G1 X174.475 Y135.800 E0.56446 F2400 ; PLA surface - infill
G1 X174.475 Y135.400 E0.01191 F2400 ; PLA surface - infill
G1 X155.525 Y135.400 E0.56446 F2400 ; PLA surface - infill
G1 X155.525 Y135.000 E0.01191 F2400 ; PLA surface - infill
G1 X174.475 Y135.000 E0.56446 F2400 ; PLA surface - infill
G1 X174.475 Y134.600 E0.01191 F2400 ; PLA surface - infill
G1 X155.525 Y134.600 E0.56446 F2400 ; PLA surface - infill
G1 X155.525 Y134.200 E0.01191 F2400 ; PLA surface - infill
G1 X174.475 Y134.200 E0.56446 F2400 ; PLA surface - infill
G1 X174.475 Y133.800 E0.01191 F2400 ; PLA surface - infill
G1 X155.525 Y133.800 E0.56446 F2400 ; PLA surface - infill
G1 X155.525 Y133.400 E0.01191 F2400 ; PLA surface - infill
G1 X174.475 Y133.400 E0.56446 F2400 ; PLA surface - infill
G1 X174.475 Y133.000 E0.01191 F2400 ; PLA surface - infill
G1 X155.525 Y133.000 E0.56446 F2400 ; PLA surface - infill
G1 X155.525 Y132.600 E0.01191 F2400 ; PLA surface - infill
G1 X174.475 Y132.600 E0.56446 F2400 ; PLA surface - infill
G1 X174.475 Y132.200 E0.01191 F2400 ; PLA surface - infill
G1 X155.525 Y132.200 E0.56446 F2400 ; PLA surface - infill
G1 X155.525 Y131.800 E0.01191 F2400 ; PLA surface - infill
G1 X174.475 Y131.800 E0.56446 F2400 ; PLA surface - infill
G1 X174.475 Y131.400 E0.01191 F2400 ; PLA surface - infill
G1 X155.525 Y131.400 E0.56446 F2400 ; PLA surface - infill
G1 X155.525 Y131.000 E0.01191 F2400 ; PLA surface - infill
G1 X174.475 Y131.000 E0.56446 F2400 ; PLA surface - infill
G1 X174.475 Y130.600 E0.01191 F2400 ; PLA surface - infill
G1 X155.525 Y130.600 E0.56446 F2400 ; PLA surface - infill
G1 X155.525 Y130.200 E0.01191 F2400 ; PLA surface - infill
G1 X174.475 Y130.200 E0.56446 F2400 ; PLA surface - infill
G1 X174.475 Y129.800 E0.01191 F2400 ; PLA surface - infill
G1 X155.525 Y129.800 E0.56446 F2400 ; PLA surface - infill
G1 X155.525 Y129.400 E0.01191 F2400 ; PLA surface - infill
G1 X174.475 Y129.400 E0.56446 F2400 ; PLA surface - infill
G1 X174.475 Y129.000 E0.01191 F2400 ; PLA surface - infill
G1 X155.525 Y129.000 E0.56446 F2400 ; PLA surface - infill
G1 X155.525 Y128.600 E0.01191 F2400 ; PLA surface - infill
G1 X174.475 Y128.600 E0.56446 F2400 ; PLA surface - infill
G1 X174.475 Y128.200 E0.01191 F2400 ; PLA surface - infill
G1 X155.525 Y128.200 E0.56446 F2400 ; PLA surface - infill
G1 X155.525 Y127.800 E0.01191 F2400 ; PLA surface - infill
G1 X174.475 Y127.800 E0.56446 F2400 ; PLA surface - infill
G1 X174.475 Y127.400 E0.01191 F2400 ; PLA surface - infill
G1 X155.525 Y127.400 E0.56446 F2400 ; PLA surface - infill
G1 X155.525 Y127.000 E0.01191 F2400 ; PLA surface - infill
G1 X174.475 Y127.000 E0.56446 F2400 ; PLA surface - infill
G1 X174.475 Y126.600 E0.01191 F2400 ; PLA surface - infill
G1 X155.525 Y126.600 E0.56446 F2400 ; PLA surface - infill
G1 X155.525 Y126.200 E0.01191 F2400 ; PLA surface - infill
G1 X174.475 Y126.200 E0.56446 F2400 ; PLA surface - infill
G1 X174.475 Y125.800 E0.01191 F2400 ; PLA surface - infill
G1 X155.525 Y125.800 E0.56446 F2400 ; PLA surface - infill
G1 X155.525 Y125.400 E0.01191 F2400 ; PLA surface - infill
G1 X174.475 Y125.400 E0.56446 F2400 ; PLA surface - infill
G1 X174.475 Y125.000 E0.01191 F2400 ; PLA surface - infill
G1 X155.525 Y125.000 E0.56446 F2400 ; PLA surface - infill
G1 X155.525 Y124.600 E0.01191 F2400 ; PLA surface - infill
G1 X174.475 Y124.600 E0.56446 F2400 ; PLA surface - infill
G1 X174.475 Y124.200 E0.01191 F2400 ; PLA surface - infill
G1 X155.525 Y124.200 E0.56446 F2400 ; PLA surface - infill
G1 X155.525 Y123.800 E0.01191 F2400 ; PLA surface - infill
G1 X174.475 Y123.800 E0.56446 F2400 ; PLA surface - infill
G1 X174.475 Y123.400 E0.01191 F2400 ; PLA surface - infill
G1 X155.525 Y123.400 E0.56446 F2400 ; PLA surface - infill
G1 X155.525 Y123.000 E0.01191 F2400 ; PLA surface - infill
G1 X174.475 Y123.000 E0.56446 F2400 ; PLA surface - infill
G1 X174.475 Y122.600 E0.01191 F2400 ; PLA surface - infill
G1 X155.525 Y122.600 E0.56446 F2400 ; PLA surface - infill
G1 X155.525 Y122.200 E0.01191 F2400 ; PLA surface - infill
G1 X174.475 Y122.200 E0.56446 F2400 ; PLA surface - infill
G1 X174.475 Y121.800 E0.01191 F2400 ; PLA surface - infill
G1 X155.525 Y121.800 E0.56446 F2400 ; PLA surface - infill
G1 X155.525 Y121.400 E0.01191 F2400 ; PLA surface - infill
G1 X174.475 Y121.400 E0.56446 F2400 ; PLA surface - infill
G1 X174.475 Y121.000 E0.01191 F2400 ; PLA surface - infill
G1 X155.525 Y121.000 E0.56446 F2400 ; PLA surface - infill
G1 X155.525 Y120.600 E0.01191 F2400 ; PLA surface - infill
G1 X174.475 Y120.600 E0.56446 F2400 ; PLA surface - infill
G1 E-0.80000 F1200 ; retract
G1 X172.975 Y120.600 F1200 ; wipe 1
G1 X174.475 Y120.600 F1200 ; wipe 2
G0 X174.475 Y120.600 Z0.400 E0.0 F6000 ; lift Z
; print surface - conductive - end

; --- Tool change: T3 -> T1 : PLA -> TPU - start
; play sound
M300 S1000 P1000
G4 P500
M300 S1000 P1000
T-1 ; unload current tool
M106 P8 S0 ; turn off fan for current tool
T1 ; load next tool
M116 P1 ; wait for extruder to reach temp.
M106 P4 S0.3 ; turn on PCF for mounted tool
M98 P"prime.g" ; prime extruder
; --- Tool change: T3 -> T1 : PLA -> TPU - end

; print surface - piezoelectric - start
G0 X172.350 Y137.290 Z0.500 E0.0 F30000 ; move over print point
G0 X172.350 Y137.290 Z0.300 E0.0 F6000 ; lower Z
G1 E3.00000 F900 ; unretract
G1 X172.350 Y122.710 E0.40551 F1200 ; TPU surface - infill
G1 X171.930 Y122.710 E0.01168 F1200 ; TPU surface - infill
G1 X171.930 Y137.290 E0.40551 F1200 ; TPU surface - infill
G1 X171.510 Y137.290 E0.01168 F1200 ; TPU surface - infill
G1 X171.510 Y122.710 E0.40551 F1200 ; TPU surface - infill
G1 X171.090 Y122.710 E0.01168 F1200 ; TPU surface - infill
G1 X171.090 Y137.290 E0.40551 F1200 ; TPU surface - infill
G1 X170.670 Y137.290 E0.01168 F1200 ; TPU surface - infill
G1 X170.670 Y122.710 E0.40551 F1200 ; TPU surface - infill
G1 X170.250 Y122.710 E0.01168 F1200 ; TPU surface - infill
G1 X170.250 Y137.290 E0.40551 F1200 ; TPU surface - infill
G1 X169.830 Y137.290 E0.01168 F1200 ; TPU surface - infill
G1 X169.830 Y122.710 E0.40551 F1200 ; TPU surface - infill
G1 X169.410 Y122.710 E0.01168 F1200 ; TPU surface - infill
G1 X169.410 Y137.290 E0.40551 F1200 ; TPU surface - infill
G1 X168.990 Y137.290 E0.01168 F1200 ; TPU surface - infill
G1 X168.990 Y122.710 E0.40551 F1200 ; TPU surface - infill
G1 X168.570 Y122.710 E0.01168 F1200 ; TPU surface - infill
G1 X168.570 Y137.290 E0.40551 F1200 ; TPU surface - infill
G1 X168.150 Y137.290 E0.01168 F1200 ; TPU surface - infill
G1 X168.150 Y122.710 E0.40551 F1200 ; TPU surface - infill
G1 X167.730 Y122.710 E0.01168 F1200 ; TPU surface - infill
G1 X167.730 Y137.290 E0.40551 F1200 ; TPU surface - infill
G1 X167.310 Y137.290 E0.01168 F1200 ; TPU surface - infill
G1 X167.310 Y122.710 E0.40551 F1200 ; TPU surface - infill
G1 X166.890 Y122.710 E0.01168 F1200 ; TPU surface - infill
G1 X166.890 Y137.290 E0.40551 F1200 ; TPU surface - infill
G1 X166.470 Y137.290 E0.01168 F1200 ; TPU surface - infill
G1 X166.470 Y122.710 E0.40551 F1200 ; TPU surface - infill
G1 X166.050 Y122.710 E0.01168 F1200 ; TPU surface - infill
G1 X166.050 Y137.290 E0.40551 F1200 ; TPU surface - infill
G1 X165.630 Y137.290 E0.01168 F1200 ; TPU surface - infill
G1 X165.630 Y122.710 E0.40551 F1200 ; TPU surface - infill
G1 X165.210 Y122.710 E0.01168 F1200 ; TPU surface - infill
G1 X165.210 Y137.290 E0.40551 F1200 ; TPU surface - infill
G1 X164.790 Y137.290 E0.01168 F1200 ; TPU surface - infill
G1 X164.790 Y122.710 E0.40551 F1200 ; TPU surface - infill
G1 X164.370 Y122.710 E0.01168 F1200 ; TPU surface - infill
G1 X164.370 Y137.290 E0.40551 F1200 ; TPU surface - infill
G1 X163.950 Y137.290 E0.01168 F1200 ; TPU surface - infill
G1 X163.950 Y122.710 E0.40551 F1200 ; TPU surface - infill
G1 X163.530 Y122.710 E0.01168 F1200 ; TPU surface - infill
G1 X163.530 Y137.290 E0.40551 F1200 ; TPU surface - infill
G1 X163.110 Y137.290 E0.01168 F1200 ; TPU surface - infill
G1 X163.110 Y122.710 E0.40551 F1200 ; TPU surface - infill
G1 X162.690 Y122.710 E0.01168 F1200 ; TPU surface - infill
G1 X162.690 Y137.290 E0.40551 F1200 ; TPU surface - infill
G1 X162.270 Y137.290 E0.01168 F1200 ; TPU surface - infill
G1 X162.270 Y122.710 E0.40551 F1200 ; TPU surface - infill
G1 X161.850 Y122.710 E0.01168 F1200 ; TPU surface - infill
G1 X161.850 Y137.290 E0.40551 F1200 ; TPU surface - infill
G1 X161.430 Y137.290 E0.01168 F1200 ; TPU surface - infill
G1 X161.430 Y122.710 E0.40551 F1200 ; TPU surface - infill
G1 X161.010 Y122.710 E0.01168 F1200 ; TPU surface - infill
G1 X161.010 Y137.290 E0.40551 F1200 ; TPU surface - infill
G1 X160.590 Y137.290 E0.01168 F1200 ; TPU surface - infill
G1 X160.590 Y122.710 E0.40551 F1200 ; TPU surface - infill
G1 X160.170 Y122.710 E0.01168 F1200 ; TPU surface - infill
G1 X160.170 Y137.290 E0.40551 F1200 ; TPU surface - infill
G1 X159.750 Y137.290 E0.01168 F1200 ; TPU surface - infill
G1 X159.750 Y122.710 E0.40551 F1200 ; TPU surface - infill
G1 X159.330 Y122.710 E0.01168 F1200 ; TPU surface - infill
G1 X159.330 Y137.290 E0.40551 F1200 ; TPU surface - infill
G1 X158.910 Y137.290 E0.01168 F1200 ; TPU surface - infill
G1 X158.910 Y122.710 E0.40551 F1200 ; TPU surface - infill
G1 X158.490 Y122.710 E0.01168 F1200 ; TPU surface - infill
G1 X158.490 Y137.290 E0.40551 F1200 ; TPU surface - infill
G1 X158.070 Y137.290 E0.01168 F1200 ; TPU surface - infill
G1 X158.070 Y122.710 E0.40551 F1200 ; TPU surface - infill
G1 X157.650 Y122.710 E0.01168 F1200 ; TPU surface - infill
G1 X157.650 Y137.290 E0.40551 F1200 ; TPU surface - infill
G1 E-3.00000 F900 ; retract
G1 X157.650 Y135.790 F900 ; wipe 1
G1 X157.650 Y137.290 F900 ; wipe 2
G0 X157.650 Y137.290 Z0.500 E0.0 F6000 ; lift Z
; print surface - piezoelectric - end

; --- Tool unload: T1 - start
T-1 ; unload current tool
M106 P4 S0 ; turn off PCF for dismounted tool
; --- Tool unload: T1 - end

; printer stop
G91 ; use relative positioning
G1 Z10 F1000 ; drop Bed 10mm
G90 ; use absolute positioning
T-1 ; unload tool
M106 P8 S0 ; turn off PCF for mounted tool
G29 S2 ; disable mesh compensation.
G1 X-30 Y180 F10000 ; park gantry at back-left of machine
M0 ; stop all
; play sound
M300 S1700 P1000
G4 P300
M300 S1700 P1000
G4 P300
M300 S1700 P1000
G4 P300
M300 S1700 P1000
G4 P300
M300 S1700 P1000
G4 P300
M300 S1700 P1000
G4 P300
M300 S1700 P1000
G4 P300
M300 S1700 P1000
