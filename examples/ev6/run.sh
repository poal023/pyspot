#!/bin/bash

# This script runs PySpot using HotSpot's example configuration for
# an EV6 Alpha processor.

PYSPOT_DIR="../../pyspot"
FLP="./ev6.flp"
PTRACE="gcc.ptrace"
HOTSPOT_CONFIG="./example.config"
OUTPUT_FILE="ev6-steady"

python3 ${PYSPOT_DIR}/pyspot.py --floorplan ${FLP} \
    --config ${HOTSPOT_CONFIG} --ptrace \
    ${PTRACE} --output ${OUTPUT_FILE} -ss
