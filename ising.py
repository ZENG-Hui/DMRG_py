import numpy as np
import basicOperations as bops
import tensornetwork as tn
import PEPS as peps

beta = 1
d = 2

baseTensor = np.zeros((d, d, d), dtype=complex)
for i in range(d):
    baseTensor[i, 0, i] = np.sqrt(np.cosh(beta))
for i in range(d):
    baseTensor[i, 1, i] = np.sqrt(np.sinh(beta)) * (1 - 2 * i) # sigma_z

base = tn.Node(baseTensor)

A = bops.multiContraction(bops.multiContraction(bops.multiContraction(
    base, base, '2', '0'), base, '3', '0', cleanOriginal1=True), base, '4', '0', cleanOriginal1=True)
AEnv = tn.Node(np.trace(A.get_tensor(), axis1=0, axis2=5))

GammaTensor = np.zeros((d**2, d, d**2), dtype=complex)
GammaTensor[1, 1, 2] = 1
GammaTensor[2, 0, 3] = 1
GammaTensor[3, 1, 0] = 1
GammaTensor[0, 0, 1] = 1
LambdaTensor = np.eye(d**2, dtype=complex)
c, d, cA, dB = peps.getBMPSRowOps(tn.Node(GammaTensor), tn.Node(LambdaTensor), tn.Node(GammaTensor), tn.Node(LambdaTensor), AEnv, AEnv, 50)
dm = peps.bmpsDensityMatrix(c, d, cA, dB, AEnv, AEnv, A, A, 50)