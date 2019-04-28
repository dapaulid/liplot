#!/usr/bin/env python

import random
import time
import math

CHANNELS = [
	('time',   lambda t: t, 's'),
	('random', lambda t: random.uniform(0, 1), 'mm'), 
	('sine',   lambda t: math.sin(2*math.pi*t), 'V'),
	('cosine', lambda t: math.cos(2*math.pi*t), 'V'),
	#('para', lambda t: 3*t*t-2*t+1, 's'),
]

INTERVAL   = 0.025 # [s]
SEPARATOR  = '\t'

# output headers
print(SEPARATOR.join(ch[0] for ch in CHANNELS))

# output data
t = 0.0 # [s]
while True:
	print(SEPARATOR.join("%f" % ch[1](t) for ch in CHANNELS))
	time.sleep(INTERVAL)
	t += INTERVAL
# end while
