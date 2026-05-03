from hotspot_config.hotspot_config import HotSpotConfig
from hotspot_solver.hotspot_solver import HotSpotSolver

import argparse

def main():
    parser = argparse.ArgumentParser(
            description="PySpot - Implementation of HotSpot in Python",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("-f", "--floorplan",
                        type=str,
                        required=True,
                        help="Floorplan file")
    parser.add_argument("-p", "--ptrace",
                        type=str,
                        required=True,
                        help="Power trace file")
    parser.add_argument("-c", "--config",
                        type=str,
                        required=True,
                        help="Configuration file")
    parser.add_argument("-ss", "--steady-state",
                        action="store_true",
                        help="Enable steady-state analysis"
                        )
    parser.add_argument("-ms", "--matrix-solver",
                        choices=["numpy", "GMRES", "LU", "QR"],
                        default="numpy",
                        help="""Algorithm to solve for the sparse system. Must
                        be 'numpy', 'GMRES', 'LU', or 'QR'""")
    parser.add_argument('--output',
                        type=str,
                        default='pyspot',
                        help='Temperature Trace Output')
    args = parser.parse_args()
    cfg = HotSpotConfig(args.config, args.floorplan, None)
    s = HotSpotSolver(cfg, args.ptrace, args.output, args.steady_state,
                      args.matrix_solver, 1e-2)
    s.solve("bkwd_euler")

if __name__ == "__main__":
    main()
