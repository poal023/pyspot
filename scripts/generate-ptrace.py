#!/usr/bin/env python3

import sys
import math
import random

def generate_dgemm_ptrace(flp_filename, ptrace_filename, timesteps=1000, dt=0.0001):
    components = []
    
    # 1. Extract component names from the floorplan
    # HotSpot requires the first line of the ptrace to exactly match the order of blocks
    try:
        with open(flp_filename, "r") as fp:
            for line in fp:
                if line.strip() == "" or line.startswith('#'):
                    continue
                parts = line.split()
                if len(parts) >= 5:
                    components.append(parts[0])
    except FileNotFoundError:
        print(f"Error: Could not find floorplan file '{flp_filename}'")
        sys.exit(1)

    print(f"Loaded {len(components)} components from floorplan.")

    # 2. Define baseline peak power for different unit types (in Watts)
    # These are heuristic weights tailored to a 250W TDP GPU running DGEMM
    power_weights = {
        "FP_INT_Execution_Block": 0.60,  # Heavy FP64 math
        "REG_FILE": 0.35,                # High operand read/write
        "L1_Data": 0.40,                 # Shared memory tile loads
        "L1_Inst": 0.10,                 # Instruction cache
        "L0_ICACHE": 0.05,
        "WARP_SCHED": 0.05,
        "DISP_UNIT": 0.05,
        "LDST": 0.15,                    # Memory operations
        "L2_Cache": 2.50,                # Monolithic L2 blocks handle massive bandwidth
        "Tensor": 0.01,                  # Idle/Leakage during standard DGEMM
        "Tex": 0.01,                     # Idle/Leakage
        "SFU": 0.01,                     # Idle/Leakage
        "Wrapper": 0.00                  # Virtual container, no power
    }

    # 3. Generate the trace
    with open(ptrace_filename, "w") as out_fp:
        # Write the header line (component names separated by tabs)
        out_fp.write("\t".join(components) + "\n")

        # Generate power for each timestep
        for t in range(timesteps):
            time_val = t * dt
            
            # Simulate alternating kernel phases using a sine wave
            # When compute_phase is high, memory_phase is low
            phase_wave = (math.sin(t * 0.1) + 1) / 2.0 
            compute_multiplier = 0.5 + (0.5 * phase_wave)       # Ranges 0.5 to 1.0
            memory_multiplier = 0.5 + (0.5 * (1.0 - phase_wave)) # Ranges 0.5 to 1.0

            row_powers = []
            
            for comp in components:
                # Determine what type of block this is
                base_power = 0.01 # default leakage
                comp_type = "Unknown"

                for key, weight in power_weights.items():
                    if key in comp:
                        base_power = weight
                        comp_type = key
                        break
                
                # Apply the phase multipliers based on the component type
                current_power = base_power
                
                if comp_type in ["FP_INT_Execution_Block", "REG_FILE", "WARP_SCHED", "DISP_UNIT", "L0_ICACHE"]:
                    current_power *= compute_multiplier
                elif comp_type in ["L1_Data", "LDST", "L2_Cache"]:
                    current_power *= memory_multiplier
                
                # Add a tiny bit of random Gaussian noise (5% variance) for realism
                if current_power > 0.0:
                    noise = random.gauss(0, 0.05 * current_power)
                    current_power = max(0.001, current_power + noise)

                # Format to 4 decimal places
                row_powers.append(f"{current_power:.4f}")

            # Write the timestep row
            out_fp.write("\t".join(row_powers) + "\n")

    print(f"Successfully generated power trace '{ptrace_filename}' with {timesteps} samples.")

if __name__ == "__main__":
    usage = """
Usage: python3 generate_ptrace.py <input.flp> <output.ptrace> [timesteps]
Example: python3 generate_ptrace.py v100_compressed.flp dgemm.ptrace 1000
    """
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print(usage)
        sys.exit(1)

    flp_file = sys.argv[1]
    ptrace_file = sys.argv[2]
    timesteps = int(sys.argv[3]) if len(sys.argv) == 4 else 1000

    generate_dgemm_ptrace(flp_file, ptrace_file, timesteps)
