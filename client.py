#!/usr/bin/env python
# -*- coding: utf-8 *-*

import socket
import struct
from objects import World, Team, Entity, Direction, dist_steps, which_way

PORT = 5000

def myrecv(s, size): ## guttenberged from joe
	data = ''
	while len(data) < size:
		data += s.recv(size - len(data))
	return data


class AntClient:

	def __init__(self, hostname, client=True, teamname='gAntZ'):

		self.world = World()
		self.tID = -1

		if len(teamname) > 16:
			teamname = teamname[:16]
		if len(teamname) < 16:
			teamname = teamname + ' '*(16-len(teamname))

		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.connect((hostname, PORT))
		self.socket.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)

		self.socket.send(struct.pack('<H16s', int(client), teamname))

		# receive first world
		self.update_world()

	def update_world(self):
		'''
		parse turn packet
		'''
		self.tID = struct.unpack('<H', myrecv(self.socket, 2))
		#print 'received tid %s' % mytid

		self.world.teams = []
		print 'scores: ',
		for tid in range(0,16):
			newteam = Team(tid)
			newteam.unpack(myrecv(self.socket, 20)) ## deserialize team
			print str(newteam.sugar)+' ',
			self.world.teams.append(newteam)

		num_of_objects = struct.unpack('<H', myrecv(self.socket, 2))
		print 'objects:%s' % num_of_objects,

		self.world.entities = []
		for _ in range(num_of_objects[0]):
			newobj = Entity(self.world)
			newobj.unpack(myrecv(self.socket, 6)) ## deserialize object
			self.world.entities.append(newobj)
		print 'ants:%d' % len(filter(lambda e: e.isant and not e.issugar, self.world.entities)),
		print 'sugars:%d' % len(filter(lambda e: not e.isant and e.issugar, self.world.entities)),
		print 'ants+sugar:%d' % len(filter(lambda e: e.isant and e.issugar, self.world.entities)),
		print 'INVALID:%d' % len(filter(lambda e: not e.isant and not e.issugar, self.world.entities))


	def find_nearest_sugar(self, a):
		sugars = world.get_sugars()

		minSugar = None
		minSteps = 1000000

		for s in sugars:
			steps = dist_steps((a.x, a.y), (s.x, s.y))
			if steps < minSteps:
				minSugar = s
				minSteps = steps

		return minSugar

	def futtersuche(self):
		my_ants = world.get_ants_for_team(self.tID)

		map(self.find_nearest_sugar, my_ants)


	def send_actions(self):
			'''
			The 'action' message:
			Offset   Type      Description
			0        u8        action for ant 0: id of field to move to: 123
			                                                             456
			...                                                          789
			15       u8        action for ant 15
			'''
			pass

if __name__ == '__main__':
	client()
