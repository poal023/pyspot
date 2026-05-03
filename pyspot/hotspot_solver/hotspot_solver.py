from hotspot_config.hotspot_config import HotSpotConfig
from hotspot_models.hotspot_block_model import HotSpotBlockModel
from hotspot_solver.hotspot_matrix_solver import HotSpotMatrixSolver
from util.util import *

import numpy as np
import pandas as pd
import time


class HotSpotSolver:
    def __init__(self, cfg, power_trace, output_file, is_steady_state,
                 matrix_solver_type="numpy", rate=1e-4):
        self._block_model = HotSpotBlockModel(cfg, is_steady_state)
        self._ptrace = pd.read_csv(power_trace,
                                   delim_whitespace=True).to_numpy()
        self._interval = rate
        self._samples = self._ptrace.shape[0]
        self._n = self._block_model._n
        self._m = self._block_model._m
        self._ambient = cfg._cfg['ambient']
        self._init_temp = cfg._cfg['init_temp']
        self._output_file = output_file
        self._mat_solver = HotSpotMatrixSolver(matrix_solver_type)

    def save_csv(self, df):
        df.to_csv(f"{self._output_file}.ttrace", sep='\t', index=False)

    def steady_state(self):
        P = np.zeros(self._m)
        P[:self._n] = np.max(self._ptrace, axis=0)
        T = self._mat_solver.solve(self._block_model._b, P)
        T = T[:self._n] + self._ambient
        df = pd.DataFrame([T], columns=[u['name'] for u in self._block_model._flp_cfg._units])
        self.save_csv(df)

    def gradT(self, T, P):
        return (self._block_model._inva * P) - (self._block_model._c_matrix @ T)

    def rk4(self, T, P, h):
        k1 = self.gradT(T, P)
        k2 = self.gradT(T + (1/2)*h * k1, P)
        k3 = self.gradT(T + (1/2)*h * k2, P)
        k4 = self.gradT(T + h * k3, P)
        return T + (h / 6) * (k1 + 2*k2 + 2*k3 + k4)

    def fwd_euler(self, T, P):
        return T + self._interval * self.gradT(T,P)

    def bkwd_euler(self, T, P):
        lhs = np.eye(self._m) + self._interval * self._block_model._c_matrix
        rhs = T + self._interval * self._block_model._inva * P
        x = self._mat_solver.solve(lhs, rhs)
        choice = self._mat_solver._choice
        return x

    def solve(self, method="fwd_euler", convergence_thresh=1e-4):
        if self._block_model._is_steady:
            return self.steady_state()

        start = time.time()
        T = np.full(self._m, self._init_temp - self._ambient)
        ttrace = np.zeros((self._samples, self._n))

        for i in range(self._samples):
            P = np.zeros(self._m)
            P[:self._n] = self._ptrace[i]
            if method == "rk4":
               dT = self.rk4(T,P,self._interval)
            elif method == "bkwd_euler":
               dT = self.bkwd_euler(T, P)
            else:
               dT = self.fwd_euler(T,P)
            T = dT
            ttrace[i] = T[:self._n] + self._ambient
        end = time.time()
        df = pd.DataFrame(ttrace, columns=[u['name'] for u in self._block_model._flp_cfg._units])
        self.save_csv(df)


