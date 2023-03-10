#!/usr/bin/env python
# -*- coding: utf-8 *-*

import struct
from pygame import Rect

ANT_HEALTH = 10
SUGAR_HEAL = 5
INITIAL_ANTS_PER_TEAM = 10


class World(object):

	__instance = None  # singleton
	nextid = 0

	BASEDIST = 200
	BASESIZE = 20
	BORDER = 90
	WORLD_SIZE = 1000

	## bases are numerated clockwise where topleft = 0
	## IMPORTANT: right and bottom boundary arent considered to be a part of the rectangle!!
	HOMEBASES = [Rect(x_y[0]-10, x_y[1]-10, 20, 20) for x_y in [(i * 200 + 100, 100) for i in range(5)]
					+ [(900, 200 * i + 300) for i in range(4)]
					+ [(700 - 200 * i, 900) for i in range(4)]
					+ [(100, 700 - i * 200) for i in range(3)]]
	@staticmethod
	def is_base(x, y):
		for (c, base) in zip(list(range(len(World.HOMEBASES))), World.HOMEBASES):
			if base.collidepoint(x, y):
				return c
		return -1

	def __new__(cls, *args, **kwargs):  # singleton
		if not cls.__instance:
			cls.__instance = super(World, cls).__new__(cls, *args, **kwargs)
		return cls.__instance

	def __init__(self):
		self.teams = []
		#self.listener = []
		#self.ants = []
		#self.sugars = [[0 for _ in xrange(WORLD_SIZE)] for _ in xrange(WORLD_SIZE)]
		self.entities = []

	def get_ants(self):
		return [e for e in self.entities if e.isant]

	def get_sugars(self):
		return [e for e in self.entities if e.issugar and not e.isant]

	def get_ants_for_team(self, teamid):
		return [e for e in self.entities if e.isant and e.tid == teamid]

	def get_team_ant(self, teamid, antid):
		return [e for e in self.entities if e.isant and e.tid == teamid and e.antid == antid]

	def search_pos(self, x, y):
		return [e for e in self.entities if e.x == x and e.y == y]


'''
Each Team (20 bytes) is coded as follows:
Offset   Type      Description
0        u16       # sugar at home base
2        u16       # remaining ants
4        16 chars  team name
'''
class Team(object):
	def __init__(self, id=-1, name=''):
		self.__id = id
		self.sugar = 0
		self.ants = INITIAL_ANTS_PER_TEAM
		self.name = name
		self.nextant = 0

	def unpack(self, teamstr):
		self.sugar, self.ants, self.name = struct.unpack('<HH16s', teamstr)

	def pack(self):
		return struct.pack('<HH16s', self.sugar, self.ants, self.name)

	def getid(self):
		return self.__id
	def setid(self, id):
		if id in range(0, 16):
			self.__id = id
	id = property(getid, setid)

	def nextantid(self):
		n=-1
		while True:
			n+=1
			yield n

	def __str__(self):
		return 'T[{},{}A,{}S,{}]'.format(self.__id, self.ants, self.sugar, self.name)


class Entity(object):
	""" Each Object (6 bytes) is coded as follows:
	Offset   Type    Description
	0        u8      upper nibble: object type (0=empty, 1=ant, 2=sugar, 3=ant+sugar), lower nibble: team ID
	1        u8      upper nibble: ant ID, lower nibble: ant health (1-10)
	2        u16     horizontal (X) coordinate
	4        u16     vertical (Y) coordinate
	"""

	FMT_STR = '<BBHH'

	def __init__(self, world):
		self.world = world
		self.x = self.y = -1
		self.isant = self.issugar = False
		self.tid = self.antid = self.anthealth = -1  # ant only

	def unpack(self, objstr):  # client & visu
		objinfo, antinfo, self.x, self.y = struct.unpack(Entity.FMT_STR, objstr)
		entitytype = objinfo >> 4
		self.isant = bool(entitytype % 2)
		self.issugar = bool((entitytype >> 1) % 2)
		self.tid = objinfo % (2 ** 4) if self.isant else -1
		self.antid = antinfo >> 4 if self.isant else -1
		self.anthealth = antinfo % (2 ** 4) if self.isant else -1

	def pack(self):  # would be user by server
		return struct.pack(Entity.FMT_STR,
		                   int(self.isant) + int(self.issugar<<1) << 4 + self.tid,
		                   self.antid << 4 + self.anthealth,
		                   self.x, self.y)

	def __str__(self):
		if self.isant:
			return 'A{}[{}??{};{}.{}]'.format(('+S' if self.issugar else ''), self.x, self.y, self.tid, self.antid)
		else:
			return 'S[{}??{}]'.format(self.x, self.y)
