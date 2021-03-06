import randomUs as ru
import sys
import pickle
import toricCode
import tensornetwork as tn
import numpy as np
import basicOperations as bops
from datetime import datetime

d = 2
M = int(sys.argv[1])
l = int(sys.argv[2])
if len(sys.argv) == 4:
    dirname = sys.argv[3]
else:
    dirname = ''

with open(dirname + 'toricBoundaries', 'rb') as f:
    [upRow, downRow, leftRow, rightRow, openA, openB] = pickle.load(f)

[cUp, dUp, te] = bops.svdTruncation(upRow, [0, 1], [2, 3], '>>')
[cDown, dDown, te] = bops.svdTruncation(downRow, [0, 1], [2, 3], '>>')

norm = toricCode.applyLocalOperators(cUp, dUp, cDown, dDown, leftRow, rightRow, toricCode.A, toricCode.B, l,
                               [tn.Node(np.eye(d)) for i in range(l * 4)])
leftRow = bops.multNode(leftRow, 1 / norm)


def expectationValue(currSites, op):
    left = leftRow
    for i in range(l):
        left = bops.multiContraction(left, cUp, '3', '0', cleanOr1=True)
        leftUp = toricCode.applyOpTosite(currSites[0][i * 2], op)
        leftDown = toricCode.applyOpTosite(currSites[1][i * 2], op)
        left = bops.multiContraction(left, leftUp, '23', '30', cleanOr1=True)
        left = bops.multiContraction(left, leftDown, '14', '30', cleanOr1=True)
        left = bops.permute(bops.multiContraction(left, dDown, '04', '21', cleanOr1=True), [3, 2, 1, 0])

        left = bops.multiContraction(left, dUp, '3', '0', cleanOr1=True)
        rightUp = toricCode.applyOpTosite(currSites[0][i * 2 + 1], op)
        rightDown = toricCode.applyOpTosite(currSites[1][i * 2 + 1], op)
        left = bops.multiContraction(left, rightUp, '23', '30', cleanOr1=True)
        left = bops.multiContraction(left, rightDown, '14', '30', cleanOr1=True)
        left = bops.permute(bops.multiContraction(left, cDown, '04', '21', cleanOr1=True), [3, 2, 1, 0])

        bops.removeState([leftUp, leftDown, rightDown, rightUp])
    return bops.multiContraction(left, rightRow, '0123', '3210').tensor * 1


proj = tn.Node(ru.proj0Tensor)
sites = [[0] * 2 * l, [0] * 2 * l]
mysum = 0
mysum2 = 0
mysum3 = 0
layers = 4
start = datetime.now()
for m in range(M * d**(4 * l)):
    sites[0][0], sites[1][0] = toricCode.verticalPair(toricCode.B, toricCode.A, cleanTop=False, cleanBottom=False)
    for layer in range(layers):
        for i in range(l):
            if layer == 0:
                rightSiteUp = toricCode.A
                rightSiteDown = toricCode.B
                cleanRight = False
            else:
                rightSiteUp = sites[0][i * 2 + 1]
                rightSiteDown = sites[1][i * 2 + 1]
                cleanRight = True
            sites[0][i * 2], sites[0][i * 2 + 1] = toricCode.horizontalPair(sites[0][i * 2], rightSiteUp, cleanRight=cleanRight)
            sites[1][i * 2], sites[1][i * 2 + 1] = toricCode.horizontalPair(sites[1][i * 2], rightSiteDown, cleanRight=cleanRight)
            if i < l - 1:
                if layer == 0:
                    rightSiteUp = toricCode.B
                    rightSiteDown = toricCode.A
                    cleanRight = False
                else:
                    rightSiteUp = sites[0][i * 2 + 2]
                    rightSiteDown = sites[1][i * 2 + 2]
                    cleanRight = True
                sites[0][i * 2 + 1], sites[0][i * 2 + 2] = toricCode.horizontalPair(sites[0][i * 2 + 1], rightSiteUp, cleanRight=cleanRight)
                sites[1][i * 2 + 1], sites[1][i * 2 + 2] = toricCode.horizontalPair(sites[1][i * 2 + 1], rightSiteDown, cleanRight=cleanRight)
            sites[0][i * 2], sites[1][i * 2] = toricCode.verticalPair(sites[0][i * 2], sites[1][i * 2])
            sites[0][i * 2], sites[1][i * 2] = toricCode.verticalPair(sites[0][i * 2], sites[1][i * 2])
        for i in range(l-1, -1, -1):
            sites[0][2 * i], sites[0][2 * i + 1] = \
                toricCode.horizontalPair(sites[0][2 * i], sites[0][2 * i + 1])
            sites[1][2 * i], sites[1][2 * i + 1] = \
                toricCode.horizontalPair(sites[1][2 * i], sites[1][2 * i + 1])
            if i > 0:
                sites[0][2 * i - 1], sites[0][2 * i] = \
                    toricCode.horizontalPair(sites[0][2 * i - 1], sites[0][2 * i])
                sites[1][2 * i - 1], sites[1][2 * i] = \
                    toricCode.horizontalPair(sites[1][2 * i - 1], sites[1][2 * i])
            sites[0][i * 2], sites[1][i * 2] = toricCode.verticalPair(sites[0][i * 2], sites[1][i * 2])
            sites[0][i * 2], sites[1][i * 2] = toricCode.verticalPair(sites[0][i * 2], sites[1][i * 2])
        norm = expectationValue(sites, tn.Node(np.eye(d)))
        sites[0][0] = bops.multNode(sites[0][0], 1 / np.sqrt(norm))
    res = expectationValue(sites, proj)
    mysum += res
    mysum2 += res ** 2
    mysum3 += res ** 3
    if m % M == M - 1:
        with open(dirname + 'global_p1_N_' + str(l * 4) + '_M_' + str(M) + '_m_' + str(m) + '_layers_' + str(layers), 'wb') as f:
            pickle.dump(mysum / (m + 1), f)
        with open(dirname + 'global_p2_N_' + str(l * 4) + '_M_' + str(M) + '_m_' + str(m) + '_layers_' + str(layers), 'wb') as f:
            pickle.dump(mysum2 / (m + 1), f)
        with open(dirname + 'global_p3_N_' + str(l * 4) + '_M_' + str(M) + '_m_' + str(m) + '_layers_' + str(layers), 'wb') as f:
            pickle.dump(mysum3 / (m + 1), f)
end = datetime.now()
with open(dirname + 'global_time_N_' + str(l * 4) + '_M_' + str(M), 'wb') as f:
    pickle.dump((end - start).total_seconds(), f)