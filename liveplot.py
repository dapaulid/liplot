#!/usr/bin/env python

from datetime import datetime
from matplotlib import pyplot
from matplotlib.animation import FuncAnimation
from random import randrange
import numpy as np
import random
import collections

CHANNELS = [
	('random', lambda t: random.uniform(0, 1), 'mm'), 
	('SIN', lambda t: np.sin(2*np.pi*t), 'V'),
	('COS', lambda t: np.cos(2*np.pi*t), 'V'),
	#('para', lambda t: 3*t*t-2*t+1, 's'),
]

WINDOWSIZE = 100 # samples
INTERVAL   = 25 # ms

FANCY = False # set to false for high performance

def mean(x):
	return sum(x) / len(x)
# end function

names = [ch[0] for ch in CHANNELS]
mononames = map(lambda s: s.ljust(len(max(names, key=len))), names)

x = collections.deque(maxlen=WINDOWSIZE)
y = []
lines = []

# hide controls, as they neither seem useful nor pretty...
pyplot.rcParams['toolbar'] = 'None'

figure, ax = pyplot.subplots()

figure.canvas.set_window_title('LivePlot')

ax.set(xlabel='time (s)', ylabel='voltage (V)',	title='voltage over time')

# hide axis ticks, as I couldn't find a way to update them when using blit=True
if not FANCY:
	figure.gca().axes.get_xaxis().set_ticks([])
	figure.gca().axes.get_yaxis().set_ticks([])
# end if

#figure.gca().axhline(linewidth=4, color='r')
figure.gca().grid()

#ax.text(0.5, 0.5, 'some text', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)

for i in range(len(CHANNELS)):
	y.append(collections.deque(maxlen=WINDOWSIZE))
	lines.append(pyplot.plot([], [])[0])
	lines[i].set_label('Label via method')
# end for

t = 0

def update(frame):
	global t
	t += INTERVAL / 1000.0

#	dx, dy = read_samples(t)

	x.append(t)
	for i in range(len(CHANNELS)):
		y[i].append(CHANNELS[i][1](t))
		lines[i].set_data(x, y[i])
		lines[i].set_label('{:s}:{: 0.3f} ({: 0.3f} |{: 0.3f} |{: 0.3f} ) {:s}'.format(
			mononames[i], y[i][-1], min(y[i]), mean(y[i]), max(y[i]), CHANNELS[i][2]))
	# end for
	leg = ax.legend(loc='lower right')
	pyplot.setp(leg.texts, family='monospace')
	figure.gca().relim()
	#figure.gca().grid()
	figure.gca().autoscale_view()
	return lines + [leg]

animation = FuncAnimation(figure, update, interval=INTERVAL, blit=not FANCY)

pyplot.show()

