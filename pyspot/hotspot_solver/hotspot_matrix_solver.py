import numpy as np

MACHINE_PRECISION=1e-6

class HotSpotMatrixSolver:
    def __init__(self,choice):
        self._choice = choice
    def solve(self, A, b, n_max=50):
        if self._choice == "GMRES":
           return self.gmres_solve(A,b, n_max)[0]
        elif self._choice == "QR":
           Q,R = self.qr_solve(A,b)
           y = Q.T @ b
           x = self.backward_sub(R, y)
           return x
        elif self._choice == "LU":
            L, U, P = self.lu_pivot(A, b)
            y = self.fwd_sub(L, P @ b)
            x = self.backward_sub(U, y)
            return x
        else:
           return self.np_solve(A,b)
    def np_solve(self, A, b):
        return np.linalg.solve(A,b)
    def gmres_solve(self, A, b, n_max):
        m = A.shape[0]
        residuals = []
        beta = np.linalg.norm(b)
        x_i = np.zeros(m)
        Q = np.zeros((m, n_max + 1))
        Hn = np.zeros((n_max + 1, n_max))
        Q[:, 0] = b / beta
        for i in range(n_max):
            v = A @ Q[:,i]
            for j in range(i + 1):
                Hn[j,i] = np.dot(Q[:,j], v)
                v = v - Hn[j,i] * Q[:,j]
            Hn[i+1,i] = np.linalg.norm(v)
            if Hn[i+1,i] != 0:
               Q[:,i+1] = v / Hn[i+1,i]
            e1 = np.zeros(i + 2)
            e1[0] = beta
            y, *_ = np.linalg.lstsq(Hn[:i+2,:i+1], e1, rcond=None)

            x_i = Q[:, :i+1] @ y
            residual = np.linalg.norm(b - A @ x_i) / beta
            residuals.append(residual)

            if residual < MACHINE_PRECISION:
               break
        return x_i, residuals
    def lu_pivot(self, A, b):
        m = A.shape[0]
        U = A.copy()
        L = np.identity(m)
        P = np.identity(m)
        for k in range(m-1):
            i = np.argmax(np.abs(U[k:,k])) + k
            U[[k,i], k:] = U[[i,k],k:]
            L[[k,i], :k] = L[[i,k],:k]
            P[[k,i], :] = P[[i,k],:]
            for j in range(k+1, m):
                L[j,k] = U[j,k] / U[k,k]
                U[j,k:] = U[j,k:] - (L[j,k] * U[k,k:])
        return L, U, P
    def fwd_sub(self, L, b):
        n = L.shape[0]
        x = np.zeros(n)
        for i in range(n):
            dot_prod = np.dot(L[i,:i], x[:i])
            x[i] = (b[i] - dot_prod) / L[i,i]
        return x
    def backward_sub(self, U, b):
        n = U.shape[0]
        x = np.zeros(n)
        for i in range(n-1, -1, -1):
            dot_prod = np.dot(U[i,i+1:], x[i+1:])
            x[i] = (b[i] - dot_prod) / U[i,i]
        return x
    def qr_solve(self, A, b):
        m,n = A.shape
        R = A.copy().astype(np.float64)
        Q = np.eye(m)

        for k in range(n):
            x = R[k:, k]
            e1 = np.zeros_like(x)
            e1[0] = 1
            v= np.sign(x[0]) * np.linalg.norm(x) * e1 + x
            v /= np.linalg.norm(v)
            R[k:,k:] = R[k:,k:] -  2 * np.outer(v, v.T @ R[k:, k:])
            Q[:, k:] = Q[:, k:] - 2 * np.outer(Q[:, k:] @ v, v.T)
        return Q,R

