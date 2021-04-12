from matplotlib import pyplot as plt
from matplotlib.tri import Triangulation
import numpy as np

def extractValues(M, N, layer):
	# create north, east, south, west arrays from QTable
	valuesN = np.reshape(layer[:, 0], (M, N))
	valuesE = np.reshape(layer[:, 1], (M, N))
	valuesS = np.reshape(layer[:, 2], (M, N))
	valuesW = np.reshape(layer[:, 3], (M, N))
	return [valuesN, valuesE, valuesS, valuesW]

def triangulation_for_triheatmap(M, N):
    xv, yv = np.meshgrid(np.arange(-0.5, M), np.arange(-0.5, N))  # vertices of the little squares
    xc, yc = np.meshgrid(np.arange(0, M), np.arange(0, N))  # centers of the little squares
    x = np.concatenate([xv.ravel(), xc.ravel()])
    y = np.concatenate([yv.ravel(), yc.ravel()])
    cstart = (M + 1) * (N + 1)  # indices of the centers

    trianglesN = [(i + j * (M + 1), i + 1 + j * (M + 1), cstart + i + j * M)
                  for j in range(N) for i in range(M)]
    trianglesE = [(i + 1 + j * (M + 1), i + 1 + (j + 1) * (M + 1), cstart + i + j * M)
                  for j in range(N) for i in range(M)]
    trianglesS = [(i + 1 + (j + 1) * (M + 1), i + (j + 1) * (M + 1), cstart + i + j * M)
                  for j in range(N) for i in range(M)]
    trianglesW = [(i + (j + 1) * (M + 1), i + j * (M + 1), cstart + i + j * M)
                  for j in range(N) for i in range(M)]
    return [Triangulation(x, y, triangles) for triangles in [trianglesN, trianglesE, trianglesS, trianglesW]]

def plotQTable(QTable, frame):
	values = extractValues(5, 5, QTable[frame*25:(frame+1)*25])
	triangul = triangulation_for_triheatmap(5, 5)
	[plt.Normalize(-0.5, 1) for _ in range(4)]
	fig, ax = plt.subplots()
	imgs = [ax.tripcolor(t, val.ravel(), cmap='RdYlGn', vmin=np.min(values), vmax=np.max(values), ec='white')
        for t, val in zip(triangul, values)]

	for val, dir in zip(values, [(-1, 0), (0, 1), (1, 0), (0, -1)]):
		for i in range(5):
			for j in range(5):
				v = val[j, i]
				nv = (v - np.min(values)) / abs(np.max(values) - np.min(values)) # normalize value to determine text color
				ax.text(i + 0.3 * dir[1], j + 0.3 * dir[0], f'{v:.2f}', color='k' if 0.2 < nv < 0.8 else 'w', ha='center', va='center')
	fig.colorbar(imgs[0], ax=ax)

	ax.set_xticks(range(5))
	ax.set_yticks(range(5))
	ax.invert_yaxis()
	ax.margins(x=0, y=0)
	ax.set_aspect('equal', 'box')  # square cells
	plt.tight_layout()
	plt.show()

def plotLineGraph(arr):
	plt.plot(arr, linestyle='-', color='red')
	plt.grid(b=True, axis='y', linestyle='--')
	plt.show()