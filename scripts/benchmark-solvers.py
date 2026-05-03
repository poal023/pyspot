import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from pyspot.util.util import DELTA
from pyspot.hotspot_solver.hotspot_matrix_solver import HotSpotMatrixSolver
import time
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline

plt.rcParams['font.size'] = 16
np.random.seed(42)

solver_type = ["numpy", "LU", "QR", "GMRES"]
input_sizes = np.array([i for i in range(10)])
baseline = 0
solver_counts = {}
for s in solver_type:
    solver_counts[s] = []
for i in input_sizes:
    n = 2**i
    A = np.random.rand(n,n)
    b = np.random.rand(n)
    for s in solver_type:
        solver = HotSpotMatrixSolver(s)
        start = time.time()
        x = solver.solve(A, b, 100)
        end = time.time()
        if s == "numpy":
           baseline = x
        error = np.linalg.norm(x - baseline) / np.linalg.norm(baseline)
        total_time = end - start
        solver_counts[s].append((total_time*1000, error))

fig, ax = plt.subplots(1,2,figsize=(10,4))

for s in solver_type:
    x_dense = np.linspace(input_sizes[0], input_sizes[-1], 40)
    spline_time = make_interp_spline(input_sizes, [t[0] for t in solver_counts[s]])
    #spline_err = make_interp_spline(input_sizes, [t[1] for t in solver_counts[s]])
    ax[0].plot(x_dense, spline_time(x_dense), label=s)
err = np.array([[t[1] for t in solver_counts[s]] for s in solver_type])
print(err)
for i,row in enumerate(err):
    if solver_type[i] == "GMRES":
       label_str = "GMRES (n = 100)"
    else:
       label_str = solver_type[i]
    r = np.array(row)
    r = np.where(r == 0.0, 1e-18, r)
    offset = (i - 4 / 2 + 0.5) * 0.2
    ax[1].bar(np.arange(len(err[0])) + offset,
                      r, width=0.2, 
                  label=label_str,
                  alpha=0.8)
    #ax[1].plot(x_dense, spline_err(x_dense), label=s)
ax[0].set_title("Time to solution for each method", fontsize=18)
ax[0].set_xlabel("Input Size ($2^i$)")
ax[0].set_ylabel("Time to solve (ms)")
ax[0].legend()
ax[1].set_ylabel("Error (log-scale)")
ax[1].set_xlabel("Input Size ($2^i$)")
ax[1].set_title("Error of solutions (v. Numpy)", fontsize=18)
ax[1].legend()
ax[1].set_yscale('log')

plt.legend()
plt.show()
