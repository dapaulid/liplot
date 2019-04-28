#!/usr/bin/env python

import random
import time
import math
import sys

CHANNELS = [
	('time',   lambda t: t, 's'),
	('random', lambda t: random.uniform(0, 1), 'mm'), 
	('sine',   lambda t: math.sin(2*math.pi*t), 'V'),
	('cosine', lambda t: math.cos(2*math.pi*t), 'V'),
	#('para', lambda t: 3*t*t-2*t+1, 's'),
]

INTERVAL   = 0.025 # [s]
SEPARATOR  = '\t'

# see if liveplot can cope with some traces
print("This is a friendly hello from data generation script!")

# output headers
print(SEPARATOR.join(ch[0] for ch in CHANNELS))

# output data
t = 0.0 # [s]
cnt = 0
while True:
	print(SEPARATOR.join("%f" % ch[1](t) for ch in CHANNELS))
	# TODO most scripts probably won't flush every time, which could
	# result in a "laggy" plot
	# as a workaround, the "unbuffer" command (apt install tcl8.6 expect)
	# could be prepended before the script
	#sys.stdout.flush() 	
	
	time.sleep(INTERVAL)
	t += INTERVAL
	cnt += 1
	
	# see if liveplot can cope with some traces
	if cnt % 100 == 0:
		print("Generated %d samples so far." % cnt)
	# end if
	
# end while
