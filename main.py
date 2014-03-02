#!/usr/bin/env python
# -*- coding: utf-8 *-*

import sys

from client import AntClient, dist_steps, which_way
from vis import Vis


def get_my_ants(client):
	return client.world.get_ants_for_team(client.tID)

def find_nearest_sugar(client, ant):
	sugars = client.world.get_sugars()
	minSugar, minSteps  = None, 1000

	for s in sugars:
		steps = dist_steps((ant.x, ant.y), (s.x, s.y))
		if steps < minSteps:
			minSugar = s
			minSteps = steps

	return minSugar ## None if no sugar in world

def futtersuche_focus(client):
	myants = get_my_ants(client)
	print 'client ID {} has {} ants'.format(client.tID, len(myants))
	for a in myants:
		s = find_nearest_sugar(client, a)
		a.move2focus((s.x,s.y))

def main():

	if len(sys.argv) < 2:
		sys.exit(1)

	client = AntClient(sys.argv[1], True)  ## here happens the network stuff in the AntClient ctor

	vis = Vis(client)
	client.update_world()

	while True:
		client.update_world()

		### some introspection
		clientTID = client.tID
		print 'client tID: %d' % clientTID

		futtersuche_focus(client)
		client.move2focuses() # move SE when no focuses set
		vis.update()


if __name__ == '__main__':
	main()
