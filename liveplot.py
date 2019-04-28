#!/usr/bin/env python

from datetime import datetime
from matplotlib import pyplot
from matplotlib.animation import FuncAnimation
from random import randrange
import numpy as np
import random
import collections
import sys
import threading
import Queue
import time
import os

WINDOWSIZE = 100 # samples
INTERVAL   = 25 # ms
QUEUE_SIZE = 32 # entries
FANCY = False # set to false for high performance

def mean(x):
	return sum(x) / len(x)
# end function

data_queue = Queue.Queue(maxsize=QUEUE_SIZE)

def consume_stdin():
	while True:
		sample = [float(s) for s in sys.stdin.readline().split()]
		data_queue.put(sample)
	# end while
# end function


print("Waiting for channel names...")
names = sys.stdin.readline().split()
num_channels = len(names)-1
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

for i in range(num_channels):
	y.append(collections.deque(maxlen=WINDOWSIZE))
	lines.append(pyplot.plot([], [])[0])
# end for

def update(frame):

	# read available samples
	samples_read = 0
	while not data_queue.empty():
		sample = data_queue.get_nowait()
		dx = sample[0]
		dy = sample[1:]
		x.append(dx)
		for i in range(num_channels):
			y[i].append(dy[i])
		# end for
		data_queue.task_done()
		samples_read += 1
	# end while

	#print(samples_read)

	# handle legend
	# needs to be done every time for some reason
	leg = ax.legend(loc='lower right')
	pyplot.setp(leg.texts, family='monospace')	
	
	if samples_read > 0:
		for i in range(num_channels):
			lines[i].set_data(x, y[i])
			lines[i].set_label('{:s}:{: 0.3f} ({: 0.3f} |{: 0.3f} |{: 0.3f} ) {:s}'.format(
				mononames[i+1], y[i][-1], min(y[i]), mean(y[i]), max(y[i]), '???'))
		# end for
		figure.gca().relim()
		#figure.gca().grid()
		figure.gca().autoscale_view()
	# end if
	return lines + [leg]

t = threading.Thread(target=consume_stdin)
t.daemon = True # don't prevent program to terminate
t.start()

animation = FuncAnimation(figure, update, interval=INTERVAL, blit=not FANCY)

pyplot.show()
print("Terminated")

