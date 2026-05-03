from floorplan.floorplan import FloorplanConfig

import re

class HotSpotConfig:
    def __init__(self, cfg_filename, flp_filename, mat_filename):
        self._cfg = self.parse_config(cfg_filename)
        self._flp_cfg = FloorplanConfig(flp_filename)
        self._mat = self.parse_mat(mat_filename)

    def parse_config(self, file_path):
        c = {}

        # Relaxed regex: Looks for '-key value', allowing any non-whitespace characters for the value
        config_pattern = re.compile(r"^\s*-(?P<key>\w+)\s+(?P<value>\S+)")

        with open(file_path, 'r') as f:
            for line in f:
                # Strip comments first to prevent trailing hashes from breaking string parsing
                clean_line = line.split('#')[0].strip()
                if not clean_line:
                    continue

                match = config_pattern.match(clean_line)
                if match:
                    key = match.group('key')
                    raw_value = match.group('value')

                    # Dynamic Type Casting
                    try:
                        # If it has a decimal or exponent, it's a float
                        if '.' in raw_value or 'e' in raw_value.lower():
                            c[key] = float(raw_value)
                        else:
                            # Otherwise, try parsing as an integer (handles 0/1 booleans)
                            c[key] = int(raw_value)
                    except ValueError:
                        # If it's not a number (e.g., "avg", "center", "(null)"), keep as string
                        c[key] = raw_value

        # --- APPLY DEFAULTS ---
        # Defaults for secondary path
        c.setdefault("s_sub", 0.021)
        c.setdefault("t_sub", 0.001)
        c.setdefault("s_solder", 0.021)
        c.setdefault("t_solder", 0.00094)
        c.setdefault("s_pcb", 0.1)
        c.setdefault("t_pcb", 0.002)
        c.setdefault("r_convec_sec", 1.0)
        c.setdefault("c_convec_sec", 140.4)
        c.setdefault("t_metal", 10e-6)
        c.setdefault("t_c4", 0.0001)

        # Booleans in HotSpot are conventionally 0/1.
        # Python's False acts mathematically as 0.
        c.setdefault("model_secondary", False)
        c.setdefault("detailed_3D_used", False)
        c.setdefault("block_omit_lateral", True)

        # Strings and Ints
        c.setdefault("grid_map_mode", "center")
        c.setdefault("grid_rows", 64)
        c.setdefault("grid_cols", 64)

        # Core defaults
        c.setdefault("t_chip", 0.15e-3)
        c.setdefault("k_chip", 100.0)
        c.setdefault("p_chip", 1.75e6)
        c.setdefault("t_interface", 20e-6)
        c.setdefault("k_interface", 4.0)
        c.setdefault("p_interface", 4e6)
        c.setdefault("t_spreader", 1e-3)
        c.setdefault("k_spreader", 400.0)
        c.setdefault("p_spreader", 3.55e6)
        c.setdefault("t_sink", 6.9e-3)
        c.setdefault("k_sink", 400.0)
        c.setdefault("p_sink", 3.55e6)
        c.setdefault("s_spreader", 0.03)
        c.setdefault("s_sink", 0.06)
        c.setdefault("r_convec", 0.1)
        c.setdefault("r_convec_sec", 1.0)
        c.setdefault("c_convec", 140.4)
        c.setdefault("ambient", 318.15)
        c.setdefault("init_temp", 333.15)

        return c

    def parse_mat(self, filename):
        pass

