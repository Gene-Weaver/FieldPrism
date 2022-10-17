#!/usr/bin/python

d = {}

for l in file('/proc/mounts'):
    if l[0] == '/':
        l = l.split()
        d[l[0]] = l[1]

import pprint

pprint.pprint(d)