#!/bin/bash

# This file runs PySpot using steady-state and uses the default numpy solver.
# If you want to perform transient analysis, just take out the -ss argument.
# If you want to change the matrix solver for SS/transient,
# this can be specified via the -ms {numpy, GMRES, LU, QR} argument.

PYSPOT_DIR="../../pyspot"
FLP="./v100_compressed.flp"
PTRACE="dgemm.ptrace"
HOTSPOT_CONFIG="./v100-hotspot.config"
OUTPUT_FILE="v100-steady"

python3 ${PYSPOT_DIR}/pyspot.py --floorplan ${FLP} \
    --config ${HOTSPOT_CONFIG} --ptrace \
    ${PTRACE} --output ${OUTPUT_FILE} -ss
