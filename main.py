#!/usr/bin/env python
# -*- coding: utf-8 *-*

import sys

from client import AntClient, dist_steps, which_way
from vis import Vis
from ai import AI

def main():

	if len(sys.argv) < 2:
		sys.exit(1)

	client = AntClient(sys.argv[1], True)  ## here happens the network stuff in the AntClient ctor

	vis = Vis(client)
	ai = AI(client)

	while True:
		client.update_world()

		#print 'client tID: %d' % client.tID

		vis.update()

		ai.update_ants()
		ai.futtersuche()
		client.send_actions(ai.calc_actions())


if __name__ == '__main__':
	main()
