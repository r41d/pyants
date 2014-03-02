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


#_action = Struct("16B")
#_hello = Struct("H16s")
#_team = Struct("HH16s")
#_object = Struct("BBHH")
#_turn = Struct("h")
#_word = Struct("H")

class AntClient:

	def __init__(self, hostname, client=True, teamname='gAntZ'):

		self.world = World()
		self.tID = -1

		if len(teamname) > 16:
			teamname = teamname[:16]
		if len(teamname) < 16:
			teamname = teamname + ' '*(16-len(teamname))

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True) ## joe ^^
		self.sock.connect((hostname, PORT))
		self.sock.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)

		self.sock.send(struct.pack('<H16s', int(client), teamname))

		self.update_world() ## receive first world
		print 'received tid %s' % self.tID

	def update_world(self):
		''' parse turn packet '''
		self.tID = struct.unpack('<H', myrecv(self.sock, 2))

		self.world.teams = []
		for tid in range(0,16):
			newteam = Team(tid)
			newteam.unpack(myrecv(self.sock, 20)) ## deserialize team
			self.world.teams.append(newteam)

		num_of_objects, = struct.unpack('<H', myrecv(self.sock, 2))
		print 'objects:%s' % num_of_objects,

		self.world.entities = []
		for _ in range(num_of_objects):
			newobj = Entity(self.world)
			newobj.unpack(myrecv(self.sock, 6)) ## deserialize object
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

	def futtersuche_focus(self):
		for a in self.world.get_ants_for_team(self.tID):
			s = self.find_nearest_sugar(a)
			a.set_focus(s.x, s.y)

	def futtersuche_go(self):
		for a in self.world.get_ants_for_team(self.tID):
			a.move2focus()

	def send_actions(self):
		''' The 'action' message:
		Offset   Type      Description                                            directions
		0        u8        action for ant 0:                                         123
		...                                                                        ← 456 →
		15       u8        action for ant 15                                         789
		'''
		my_ants = self.world.get_ants_for_team(self.tID)

		for i in range(16):
			search = self.world.get_team_ant(self.tID, i)
			if len(search) > 0:
				dir = search[0].dir
			else:
				dir = Direction.NONE
			msg = struct.pack('<B', dir)
			print('send dir %s' % str(msg)),
			self.sock.send(msg)


	def send_action(self, actions):
		assert len(actions) == 16
		for a in actions:
			self.sock.send(struct.pack('<16B', *actions))



if __name__ == '__main__':
	client()
