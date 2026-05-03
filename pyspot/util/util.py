NL = 4
EXTRA = 12
K_SUB = 1.0 / 0.5
K_SOLDER = 1.0 / 0.06
K_PCB = 1.0 / 0.333
K_METAL = 1.0 / 0.0025
C_FACTOR = 0.333
SPEC_HEAT_SUB = 1.6e6
SPEC_HEAT_SOLDER = 2.1e6
SPEC_HEAT_PCB = 1.32e6
SPEC_HEAT_METAL = 3.55e6
SPEC_HEAT_C4 = 1.65e6

SP_W = 0
SP_E = 1
SP_N = 2
SP_S = 3
# Central sink nodes (directly under the spreader)
SINK_C_W = 4
SINK_C_E = 5
SINK_C_N = 6
SINK_C_S = 7
# Peripheral sink nodes
SINK_W = 8
SINK_E = 9
SINK_N = 10
SINK_S = 11
# Package substrate nodes
SUB_W = 12
SUB_E = 13
SUB_N = 14
SUB_S = 15
# Solder ball nodes
SOLDER_W = 16
SOLDER_E = 17
SOLDER_N = 18
SOLDER_S = 19
# Central PCB nodes (directly under the solder balls)
PCB_C_W = 20
PCB_C_E = 21
PCB_C_N = 22
PCB_C_S = 23
# Peripheral PCB nodes
PCB_W = 24
PCB_E = 25
PCB_N = 26
PCB_S = 27

IFACE=1
HSP=2
HSINK=3

DELTA = 1e-6

def get_resistance(conductivity, thickness, area):
    return thickness / (conductivity * area)

def get_capacitance(sp_heat, thickness, area):
    return C_FACTOR * sp_heat * thickness * area
