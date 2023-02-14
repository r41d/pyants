#!/usr/bin/env python
# -*- coding: utf-8 *-*

import sys

from client import AntClient
from vis import Vis
from ai import AI


VIS = False

def main():

	if len(sys.argv) < 2:
		print "need IP as first argument"
		sys.exit(1)

	client = AntClient(sys.argv[1], True)  # here happens the network stuff in the AntClient ctor

	if VIS: vis = Vis(client)
	ai = AI(client)

	while True:
		client.update_world()
		if VIS: vis.update()
		ai.update_ants()
		ai.perform_ai()
		client.send_actions(ai.calc_actions())

if __name__ == '__main__':
	main()
