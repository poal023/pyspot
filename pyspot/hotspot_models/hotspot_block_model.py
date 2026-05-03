from hotspot_config.hotspot_config import HotSpotConfig
from package_rc.package_rc import PackageRC
from util.util import *

import numpy as np

class HotSpotBlockModel:
    def __init__(self, hotspot_cfg, is_steady_state):
        self._hotspot_cfg = hotspot_cfg
        self._flp_cfg = hotspot_cfg._flp_cfg
        self._is_steady = is_steady_state
        self._ambient = hotspot_cfg._cfg['ambient']
        self._init_temp = hotspot_cfg._cfg['init_temp']
        self._m = NL * self._flp_cfg._n_units + EXTRA
        self._n = self._flp_cfg._n_units

        self._pack = PackageRC(hotspot_cfg)
        self.init_matrices()
        self.build_R_model()
        self.build_C_model()

    def init_matrices(self):
        self._k1 = np.zeros(self._m)
        self._k2 = np.zeros(self._m)
        self._k3 = np.zeros(self._m)
        self._k4 = np.zeros(self._m)
        self._t_rk = np.zeros(self._m)
        self._ytemp = np.zeros(self._m)
        self._t1 = np.zeros(self._m)
        self._t2 = np.zeros(self._m)
        self._tvec = np.zeros(self._m)
        self._dv = np.zeros(self._m)

    def build_R_model(self):
        t_chip = self._hotspot_cfg._cfg['t_chip']
        k_chip = self._hotspot_cfg._cfg['k_chip']
        k_interface = self._hotspot_cfg._cfg['k_interface']
        k_spreader = self._hotspot_cfg._cfg['k_spreader']
        k_sink = self._hotspot_cfg._cfg['k_sink']
        t_interface = self._hotspot_cfg._cfg['t_interface']
        t_spreader = self._hotspot_cfg._cfg['t_spreader']
        t_sink = self._hotspot_cfg._cfg['t_sink']
        r_convec = self._hotspot_cfg._cfg['r_convec']
        s_sink = self._hotspot_cfg._cfg['s_sink']
        block_omit_lateral = self._hotspot_cfg._cfg['block_omit_lateral']

        g_lateral = np.zeros((2,self._n))
        g_int = np.zeros((2,self._n))
        g_sp = np.zeros((2,self._n))
        g_hs = np.zeros((2,self._n))
        g_amb = np.zeros((self._n + EXTRA))

        for i in range(self._n):
            w = self._flp_cfg._units[i]['w']
            h = self._flp_cfg._units[i]['h']
            if block_omit_lateral:
               g_lateral[:,i] = 0
            else:
               g_lateral[0,i] = 1.0 / get_resistance(k_chip, w / 2, h * t_chip)
               g_lateral[1,i] = 1.0 / get_resistance(k_chip, h / 2, w * t_chip)
            g_int[0,i] = 1.0 / get_resistance(
                    k_interface, w / 2.0, h * t_interface
            )
            g_int[1,i] = 1.0 / get_resistance(
                    k_interface, h / 2.0, w * t_interface
            )
            g_sp[0,i] = 1.0 / get_resistance(
                    k_spreader, w / 2.0, h * t_spreader
            )
            g_sp[1,i] = 1.0 / get_resistance(
                    k_spreader, h / 2.0, w * t_spreader
            )
            g_hs[0,i] = 1.0 / get_resistance(
                    k_sink, w / 2.0, h * t_sink
            )
            g_hs[1,i] = 1.0 / get_resistance(
                    k_sink, h / 2.0, w * t_sink
            )
        length = self._flp_cfg.get_shared_lengths()
        border = np.zeros((self._n, 4), dtype=int)  # W=0, E=1, N=2, S=3
        gn_sp = gs_sp = ge_sp = gw_sp = 0.0
        gn_hs = gs_hs = ge_hs = gw_hs = 0.0

        l_chip = self._flp_cfg._height
        w_chip = self._flp_cfg._width

        for i in range(self._n):
            u = self._flp_cfg._units[i]
            # North
            if np.isclose(u['bottom_y'] + u['h'], l_chip, atol=1e-6):
                gn_sp += g_sp[1, i]
                gn_hs += g_hs[1, i]
                border[i, 2] = 1
            # South
            if np.isclose(u['bottom_y'], 0.0, atol=1e-6):
                gs_sp += g_sp[1, i]
                gs_hs += g_hs[1, i]
                border[i, 3] = 1
            # East
            if np.isclose(u['left_x'] + u['w'], w_chip, atol=1e-6):
                ge_sp += g_sp[0, i]
                ge_hs += g_hs[0, i]
                border[i, 1] = 1
            # West
            if np.isclose(u['left_x'], 0.0, atol=1e-6):
                gw_sp += g_sp[0, i]
                gw_hs += g_hs[0, i]
                border[i, 0] = 1

        g_matrix = np.zeros((self._m, self._m))
        pk = self._pack
        n = self._n

        for i in range(n):
            u_i = self._flp_cfg._units[i]
            area = u_i['h'] * u_i['w']

            for j in range(n):
                part = part_int = part_sp = part_hs = 0.0

                if length[i, j] > 0:
                    if self._flp_cfg.horizontal_adj(i, j):
                        part = g_lateral[0, i] / u_i['h']
                        part_int = g_int[0, i] / u_i['h']
                        part_sp = g_sp[0, i] / u_i['h']
                        part_hs = g_hs[0, i] / u_i['h']
                    elif self._flp_cfg.vertical_adj(i, j):
                        part = g_lateral[1, i] / u_i['w']
                        part_int = g_int[1, i] / u_i['w']
                        part_sp = g_sp[1, i] / u_i['w']
                        part_hs = g_hs[1, i] / u_i['w']

                g_matrix[i, j] = part * length[i, j]
                g_matrix[IFACE * n + i, IFACE * n + j] = part_int * length[i, j]
                g_matrix[HSP * n + i, HSP * n + j] = part_sp * length[i, j]
                g_matrix[HSINK * n + i, HSINK * n + j] = part_hs * length[i, j]

            # Vertical connections within the same block
            g_matrix[i, IFACE * n + i] = g_matrix[IFACE * n + i, i] = 2.0 / get_resistance(k_chip, t_chip, area)
            g_matrix[IFACE * n + i, HSP * n + i] = g_matrix[HSP * n + i, IFACE * n + i] = 2.0 / get_resistance(k_interface, t_interface, area)
            g_matrix[HSP * n + i, HSINK * n + i] = g_matrix[HSINK * n + i, HSP * n + i] = 2.0 / get_resistance(k_spreader, t_spreader, area)

            r_amb = r_convec * (s_sink * s_sink) / area
            g_amb[i] = 1.0 / (get_resistance(k_sink, t_sink, area) + r_amb)

            # Spreader perimeter connections
            g_matrix[HSP * n + i, NL * n + SP_N] = g_matrix[NL * n + SP_N, HSP * n + i] = (2.0 * border[i, 2] / ((1.0 / g_sp[1, i]) + pk.r_sp1_y * gn_sp / g_sp[1, i]) if g_sp[1, i] != 0 else 0.0)
            g_matrix[HSP * n + i, NL * n + SP_S] = g_matrix[NL * n + SP_S, HSP * n + i] = (2.0 * border[i, 3] / ((1.0 / g_sp[1, i]) + pk.r_sp1_y * gs_sp / g_sp[1, i]) if g_sp[1, i] != 0 else 0.0)
            g_matrix[HSP * n + i, NL * n + SP_E] = g_matrix[NL * n + SP_E, HSP * n + i] = (2.0 * border[i, 1] / ((1.0 / g_sp[0, i]) + pk.r_sp1_x * ge_sp / g_sp[0, i]) if g_sp[0, i] != 0 else 0.0)
            g_matrix[HSP * n + i, NL * n + SP_W] = g_matrix[NL * n + SP_W, HSP * n + i] = (2.0 * border[i, 0] / ((1.0 / g_sp[0, i]) + pk.r_sp1_x * gw_sp / g_sp[0, i]) if g_sp[0, i] != 0 else 0.0)

            # Sink perimeter connections
            g_matrix[HSINK * n + i, NL * n + SINK_C_N] = g_matrix[NL * n + SINK_C_N, HSINK * n + i] = (2.0 * border[i, 2] / ((1.0 / g_hs[1, i]) + pk.r_hs1_y * gn_hs / g_hs[1, i]) if g_hs[1, i] != 0 else 0.0)
            g_matrix[HSINK * n + i, NL * n + SINK_C_S] = g_matrix[NL * n + SINK_C_S, HSINK * n + i] = (2.0 * border[i, 3] / ((1.0 / g_hs[1, i]) + pk.r_hs1_y * gs_hs / g_hs[1, i]) if g_hs[1, i] != 0 else 0.0)
            g_matrix[HSINK * n + i, NL * n + SINK_C_E] = g_matrix[NL * n + SINK_C_E, HSINK * n + i] = (2.0 * border[i, 1] / ((1.0 / g_hs[0, i]) + pk.r_hs1_x * ge_hs / g_hs[0, i]) if g_hs[0, i] != 0 else 0.0)
            g_matrix[HSINK * n + i, NL * n + SINK_C_W] = g_matrix[NL * n + SINK_C_W, HSINK * n + i] = (2.0 * border[i, 0] / ((1.0 / g_hs[0, i]) + pk.r_hs1_x * gw_hs / g_hs[0, i]) if g_hs[0, i] != 0 else 0.0)

        # Global peripheral nodes
        g_matrix[NL * n + SP_N, NL * n + SINK_C_N] = g_matrix[NL * n + SINK_C_N, NL * n + SP_N] = 2.0 / pk.r_sp_per_y
        g_matrix[NL * n + SP_S, NL * n + SINK_C_S] = g_matrix[NL * n + SINK_C_S, NL * n + SP_S] = 2.0 / pk.r_sp_per_y
        g_matrix[NL * n + SP_E, NL * n + SINK_C_E] = g_matrix[NL * n + SINK_C_E, NL * n + SP_E] = 2.0 / pk.r_sp_per_x
        g_matrix[NL * n + SP_W, NL * n + SINK_C_W] = g_matrix[NL * n + SINK_C_W, NL * n + SP_W] = 2.0 / pk.r_sp_per_x

        g_matrix[NL * n + SINK_C_N, NL * n + SINK_N] = g_matrix[NL * n + SINK_N, NL * n + SINK_C_N] = 2.0 / (pk.r_hs + pk.r_hs2_y)
        g_matrix[NL * n + SINK_C_S, NL * n + SINK_S] = g_matrix[NL * n + SINK_S, NL * n + SINK_C_S] = 2.0 / (pk.r_hs + pk.r_hs2_y)
        g_matrix[NL * n + SINK_C_E, NL * n + SINK_E] = g_matrix[NL * n + SINK_E, NL * n + SINK_C_E] = 2.0 / (pk.r_hs + pk.r_hs2_x)
        g_matrix[NL * n + SINK_C_W, NL * n + SINK_W] = g_matrix[NL * n + SINK_W, NL * n + SINK_C_W] = 2.0 / (pk.r_hs + pk.r_hs2_x)

        g_amb[n + SINK_C_N] = g_amb[n + SINK_C_S] = 1.0 / (pk.r_hs_c_per_y + pk.r_amb_c_per_y)
        g_amb[n + SINK_C_E] = g_amb[n + SINK_C_W] = 1.0 / (pk.r_hs_c_per_x + pk.r_amb_c_per_x)
        g_amb[n + SINK_N] = g_amb[n + SINK_S] = g_amb[n + SINK_E] = g_amb[n + SINK_W] = 1.0 / (pk.r_hs_per + pk.r_amb_per)
        b = np.zeros((self._m, self._m))

        valid = (g_matrix > 0) & (g_matrix.T > 0)

        b[valid] = -1.0 / (1.0 / g_matrix[valid] + 1.0 / g_matrix.T[valid])

        diag_vals = np.zeros(self._m)

        diag_vals[HSINK * n : NL * n] = g_amb[:n]

        idx_start = NL * n + SINK_C_W
        amb_start = n + SINK_C_W
        diag_vals[idx_start:] = g_amb[amb_start:]

        diag_vals -= np.sum(b, axis=1)

        np.fill_diagonal(b, diag_vals)

        self._b = b
        self._g_amb = g_amb

    def build_C_model(self):
        cfg = self._hotspot_cfg._cfg
        n, m, pk = self._n, self._m, self._pack

        w = np.array([u['w'] for u in self._flp_cfg._units])
        h = np.array([u['h'] for u in self._flp_cfg._units])
        area = w * h

        a = np.zeros(m)
        
        a[:n] = get_capacitance(cfg['p_chip'], cfg['t_chip'], area)
        a[IFACE * n : HSP * n] = get_capacitance(cfg['p_interface'], cfg['t_interface'], area)
        a[HSP * n : HSINK * n] = get_capacitance(cfg['p_spreader'], cfg['t_spreader'], area)
        
        c_amb = C_FACTOR * cfg['c_convec'] / (cfg['s_sink'] ** 2) * area
        a[HSINK * n : NL * n] = get_capacitance(cfg['p_sink'], cfg['t_sink'], area) + c_amb
            
        a[NL * n + SP_N] = a[NL * n + SP_S] = pk.c_sp_per_y
        a[NL * n + SP_E] = a[NL * n + SP_W] = pk.c_sp_per_x
        a[NL * n + SINK_C_N] = a[NL * n + SINK_C_S] = (pk.c_hs_c_per_y + pk.c_amb_c_per_y)
        a[NL * n + SINK_C_E] = a[NL * n + SINK_C_W] = (pk.c_hs_c_per_x + pk.c_amb_c_per_x)
        a[NL * n + SINK_N] = a[NL * n + SINK_S] = a[NL * n + SINK_E] = a[NL * n + SINK_W] = (pk.c_hs_per + pk.c_amb_per)

        self._a = a
        self._inva = 1.0 / a
        self._c_matrix = np.diag(self._inva) @ self._b

