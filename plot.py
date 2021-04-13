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

	plt.xticks(range(5), range(1, 6))
	plt.yticks(range(5), range(1, 6))
	ax.invert_yaxis()
	ax.margins(x=0, y=0)
	ax.set_aspect('equal', 'box')  # square cells

	# put QTable description in title
	description = ''
	if frame >= 4:
		# only report dropoff locations that are full
		pd = [int(x) for x in bin(frame-4)[2:]]
		if pd[3] == 1: # first
			description += 'First'
		if pd[2] == 1: # second
			if description != '':
				description += ', second'
			else:
				description += 'Second'
		if pd[1] == 1: # third
			if description != '':
				description += ', third'
			else:
				description += 'Third'
		if pd[0] == 1: # fourth
			if description != '':
				description += ', fourth'
			else:
				description += 'Fourth'
		if description == '':
			description += 'No'
		description += ' dropoff(s) full'
	else:
		# only report pickup locations that are empty
		pd = [int(x) for x in bin(frame+4)[3:]]
		if pd[1] == 1:
			description += 'First'
		if pd[0] == 1:
			if description != '':
				description += ', second'
			else:
				description += 'Second'
		if description == '':
			description += 'No'
		description += ' pickup(s) full'

	ax.set(title=f'QTable Frame {frame+1}\n{description}')
	plt.tight_layout()
	plt.show()

def plotLineGraph(arr, title):
	fig, ax = plt.subplots()
	ax.plot(arr, linestyle='-', color='red')
	ax.set(title=title)
	ax.set_ylim(min(0, min(arr)))
	plt.grid(b=True, axis='y', linestyle='--')
	plt.show()