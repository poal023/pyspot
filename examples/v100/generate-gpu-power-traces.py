import random

def generate_dp_ptrace(flp_file, ptrace_file, num_samples=10):
    blocks = {}
    # 1. Parse floorplan to get areas (Area = W * H)
    with open(flp_file, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                parts = line.strip().split()
                if len(parts) >= 5:
                    name = parts[0]
                    area = float(parts[1]) * float(parts[2])
                    blocks[name] = area

    block_names = list(blocks.keys())
    
    # 2. Define active power densities for a DP Workload (Watts per mm^2)
    # Note: 1 m^2 = 1,000,000 mm^2. We work in W/m^2 to match the parsed floorplan dimensions.
    W_PER_M2 = 1.5e6
    
    power_densities = {
        "FP64": 2.2 * W_PER_M2,     # High utilization
        "REG_FILE": 1.2 * W_PER_M2, # High utilization (feeding 64-bit operands)
        "LDST": 0.8 * W_PER_M2,     # Memory fetches
        "L1_Data": 0.6 * W_PER_M2,  # Cache access
        "L0_ICACHE": 0.5 * W_PER_M2,
        "FP32": 0.05 * W_PER_M2,    # Mostly idle / clock-gated
        "INT": 0.05 * W_PER_M2,     # Mostly idle / loop unrolling logic only
        "Tensor": 0.01 * W_PER_M2,  # Off
        "Tex": 0.01 * W_PER_M2,     # Off
        "HBM_PHY": 0.4 * W_PER_M2,  # Memory traffic
        "PCIe": 0.1 * W_PER_M2,     # Mostly idle during compute phase
        "DEFAULT": 0.1 * W_PER_M2   # Base background leakage/clock power
    }

    with open(ptrace_file, 'w') as f:
        f.write("\t".join(block_names) + "\n")
        # Generate samples
        for _ in range(num_samples):
            total = 0
            sample_powers = []
            for name in block_names:
                # Determine block type
                density = power_densities["DEFAULT"]
                for key in power_densities:
                    if key in name:
                        density = power_densities[key]
                        break
                # Add variability into "mock" power traces
                noise = random.uniform(0.90, 1.1)
                power = blocks[name] * density * noise
                total += power
                sample_powers.append(f"{power}")
            f.write("\t".join(sample_powers) + "\n")
            print(total)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate 'dummy'
                                     GPU power-traces based on a floorplan")

    parser.add_argument("floorplan", help="Path to the input file")
    parser.add_argument("trace_output", help="Path to the output file")
    parser.add_argument("samples", type=int, help="An integer value")

    args = parser.parse_args()
    generate_dp_ptrace(args.floorplan, args.trace_output,
                       num_samples=args.samples)
    print(f"Generated {args.samples} samples to {args.trace_output}")
