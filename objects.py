#!/usr/bin/env python
# -*- coding: utf-8 *-*

import struct
from enum import Enum
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
	HOMEBASES = map(lambda (x, y): Rect(x, y, x + 20, y + 20),
	                [(i * 200 + 90, 90) for i in range(5)]
					+ [(890, 200 * i + 290) for i in range(4)]
					+ [(690 - 200 * i, 890) for i in range(4)]
					+ [(90, 690 - i * 200) for i in range(3)]
				)

	@staticmethod
	def is_base(x, y):
		for (c, base) in zip(range(len(World.HOMEBASES)), World.HOMEBASES):
			if base.collidepoint(x, y):
				return c
		return -1

	def __new__(cls, *args, **kwargs): ## singleton
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
		return filter(lambda e: e.isant, self.entities)

	def get_sugars(self):
		return filter(lambda e: e.issugar and not e.isant, self.entities)

	def get_ants_for_team(self, teamid):
		return filter(lambda e: e.isant and e.tid == teamid, self.entities)

	def get_team_ant(self, teamid, antid):
		return filter(lambda e: e.isant and e.tid == teamid and e.antid == antid, self.entities)


	def search_pos(self, x, y):
		return filter(lambda e: e.x == x and e.y == y, self.entities)

	def login(self, loginstr):
		""" Format of the 'hello' packet:
		Offset   Type      Description
		0        u16       client type (0=non-team, 1=team)
		2        16 chars  team name (if team client, else ignored) """
		isplayer, teamname = struct.unpack('<H16s', loginstr)
		if bool(isplayer):
			newteam = Team(World.nextid, teamname)
			self.teams += newteam
			for _ in range(INITIAL_ANTS_PER_TEAM):
				self.register_ant(newteam)

	def register_ant(self, team, xy=(-1,-1)):
		#assert x>0 and y>0 and x < WORLD_SIZE and y < WORLD_SIZE
		newant = Entity(self)
		newant.isant = True
		newant.tid = team.id
		newant.antid = team.nextantid()
		newant.anthealth = ANT_HEALTH

		newant.world = self
		self.ants.append(newant)

	def place_sugar(self, random=True, x=-1, y=-1):
		if random or x not in range(0, World.WORLD_SIZE) or y not in range(0, World.WORLD_SIZE):
			x = random.randint(0, World.WORLD_SIZE)
			y = random.randint(0, World.WORLD_SIZE)
		self.sugars[x][y] += 1



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
		if id in xrange(0, 16):
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
		#self.focus = self.dir = None  # ant KI only

	def unpack(self, objstr): ## client & visu
		objinfo, antinfo, self.x, self.y = struct.unpack(Entity.FMT_STR, objstr)
		entitytype = objinfo >> 4
		self.isant = bool(entitytype % 2)
		self.issugar = bool((entitytype >> 1) % 2)
		self.tid = objinfo % (2 ** 4) if self.isant else -1
		self.antid = antinfo >> 4 if self.isant else -1
		self.anthealth = antinfo % (2 ** 4) if self.isant else -1

	def pack(self): ## would be user by server
		return struct.pack(Entity.FMT_STR,
		                   int(self.isant) + int(self.issugar<<1) << 4 + self.tid,
		                   self.antid << 4 + self.anthealth,
		                   self.x, self.y)


	### methods only to be used from the client

	def move2focus(self, foc): # only use from client
		''' specify a position and we will try to get there '''
		self.focus = foc
		self.dir = which_way((self.x, self.y), self.focus)

	def __str__(self):
		if self.isant:
			print(self.focus)
			return 'A{}[{}×{};{}.{}]'.format(('+S' if self.issugar else ''), self.x, self.y, self.tid, self.antid)
		else:
			return 'S[{}×{}]'.format(self.x, self.y)


class Direction(Enum):
	NONE = 5
	NW = 1
	N = 2
	NE = 3
	E = 6
	SE = 9
	S = 8
	SW = 7
	W = 4


def dist_steps((x1,y1), (x2,y2)):
	xB = max(x1,x2)
	xS = min(x1,x2)
	yB = max(y1,y2)
	yS = min(y1,y2)
	steps = 0
	while xS < xB and yS < yB:
		xS, yS = xS+1, yS+1
		steps += 1
	while xS < xB:
		xS += 1
		steps += 1
	while yS < yB:
		yS += 1
		steps += 1
	return steps

def which_way((x, y), (goalX, goalY)):
	if x < goalX and y < goalY: return Direction.SE
	if x < goalX and y > goalY: return Direction.NE
	if x > goalX and y < goalY: return Direction.SW
	if x > goalX and y > goalY: return Direction.NW
	if x < goalX: return Direction.E
	if x > goalX: return Direction.W
	if y < goalY: return Direction.N
	if y > goalY: return Direction.S
	return Direction.NONE
