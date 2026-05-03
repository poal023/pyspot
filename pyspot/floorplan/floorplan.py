import numpy as np
from util.util import *

class FloorplanConfig:
    def __init__(self, flp_filename):
        self._units = []
        self.parse_floorplan(flp_filename)
        self._n_units = len(self._units)
        self._width = self.get_chip_width()
        self._height = self.get_chip_height()

    def horizontal_adj(self, i, j):
        a = self._units[i]
        b = self._units[j]
        return (
                (np.isclose(a['left_x'] + a['w'], b['left_x'], atol=DELTA,
                            rtol=0)
                or np.isclose(b['left_x'] + b['w'], a['left_x'],
                              atol=DELTA, rtol=0))
                and not (a['bottom_y'] + a['h'] <= b['bottom_y'] + DELTA
                         or b['bottom_y'] + b['h'] <= a['bottom_y'] + DELTA
                )
        )
    def vertical_adj(self, i, j):
        a = self._units[i]
        b = self._units[j]
        return (
                (np.isclose(a['bottom_y'] + a['h'], b['bottom_y'], atol=DELTA,
                            rtol=0)
                or np.isclose(b['bottom_y'] + b['h'], a['bottom_y'],
                              atol=DELTA, rtol=0))
                and not (a['left_x'] + a['w'] <= b['left_x'] + DELTA
                         or b['left_x'] + b['w'] <= a['left_x'] + DELTA
                )
        )
    def get_shared_lengths(self):
        length = np.zeros((self._n_units, self._n_units))

        x = [u['left_x'] for u in self._units]
        y = [u['bottom_y'] for u in self._units]
        w = [u['w'] for u in self._units]
        h = [u['h'] for u in self._units]

        for i in range(self._n_units):
            xi, yi, wi, hi = x[i], y[i], w[i], h[i]

            for j in range(i + 1, self._n_units):
                xj, yj, wj, hj = x[j], y[j], w[j], h[j]

                if abs((xi + wi) - xj) <= DELTA or abs((xj + wj) - xi) <= DELTA:
                    if not (yi + hi <= yj + DELTA or yj + hj <= yi + DELTA):
                        y_min = yi if yi > yj else yj
                        y_max = yi + hi if yi + hi < yj + hj else yj + hj
                        val = y_max - y_min
                        if val > 0:
                            length[i, j] = length[j, i] = val
                        continue 

                if abs((yi + hi) - yj) <= DELTA or abs((yj + hj) - yi) <= DELTA:
                    if not (xi + wi <= xj + DELTA or xj + wj <= xi + DELTA):
                        x_min = xi if xi > xj else xj
                        x_max = xi + wi if xi + wi < xj + wj else xj + wj
                        val = x_max - x_min
                        if val > 0:
                            length[i, j] = length[j, i] = val

        return length

    def get_chip_width(self):
        if not self._n_units:
            return 0.0
        return (
                max(u['left_x'] + u['w'] for u in self._units) -
                min(u['left_x'] for u in self._units)
        )
    def get_chip_height(self):
        if not self._n_units:
            return 0.0
        return (
                max(u['bottom_y'] + u['h'] for u in self._units) -
                min(u['bottom_y'] for u in self._units)
        )

    def parse_floorplan(self, filename):
        with open(filename, 'r') as f:
            for line_num, line in enumerate(f, 1):
                clean_line = line.split('#')[0].strip()
                if not clean_line:
                    continue

                parts = clean_line.split()

                if len(parts) != 5:
                    raise SyntaxError(f"FLP Error (Line {line_num}): Expected 5 columns, got {len(parts)}")

                try:
                    name = parts[0]
                    coords = [float(x) for x in parts[1:]]

                    if coords[0] < 0 or coords[1] < 0:
                        raise ValueError(f"FLP Error (Line {line_num}): Dimensions must be positive.")

                    self._units.append({'name': name, 'w': coords[0], 'h':
                                        coords[1], 'left_x': coords[2],
                                        'bottom_y': coords[3]})
                except ValueError:
                    raise ValueError(f"FLP Error (Line {line_num}): Coordinates must be numeric.")

