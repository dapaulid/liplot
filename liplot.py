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

SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0]

def mean(x):
	return sum(x) / len(x)
# end function

def trace(msg):
	print("[%s] %s" % (SCRIPT_NAME, msg))
# end function

data_queue = Queue.Queue(maxsize=QUEUE_SIZE)

def try_parse_sample(line):
	try:
		return [float(col) for col in line.split()]
	except ValueError:
		return None
	# end if
# end def

def consume_stdin():
	while True:
		line = sys.stdin.readline()
		sample = try_parse_sample(line)
		if sample:
			data_queue.put(sample)
		else:
			# forward
			sys.stdout.write(line)
		# end if
	# end while
# end function


trace("waiting for data...")
last_line = None
while True:
	line = sys.stdin.readline()
	first_sample = try_parse_sample(line)
	if first_sample:
		n = len(first_sample)
		num_channels = n-1
		# check for headers
		names = last_line.split()
		if len(names) != n:
			# not matching, no channel names
			names = [None] * len(first_sample)
		# end if
		data_queue.put(first_sample)
		break
	else:
		# forward
		sys.stdout.write(line)
	# end if
	last_line = line
# end while

#names = sys.stdin.readline().split()
#num_channels = len(names)-1
labels = [s.ljust(len(max(names, key=len)))+':' if s != None else '' for s in names]

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
			lines[i].set_label('{:s}{: 0.3f} ({: 0.3f} |{: 0.3f} |{: 0.3f} )'.format(
				labels[i+1], y[i][-1], min(y[i]), mean(y[i]), max(y[i])))
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

try:
	pyplot.show()
	trace("terminated")
except KeyboardInterrupt:
	trace("keyboard interrupt")
# end try

