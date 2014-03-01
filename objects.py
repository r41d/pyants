#!/usr/bin/env python
# -*- coding: utf-8 *-*

import struct

ANT_HEALTH = 10
SUGAR_HEAL = 5
INITIAL_ANTS_PER_TEAM = 10

class World(object):

	__instance = None ## singleton
	nextid = 0

	WORLD_SIZE = 1000

	## AH, FUCK, bases are numerated clockwise, fix that later
	HOMEBASES = list(map(lambda (x,y): (x,y,x+20,y+20),
	                [(x, 90) for x in range(90, 891, 200)]
					+ [(x,y) for x in [90,890] for y in [290,490,690]]
					+ [(x,890) for x in range(90,891,200)]))

	def __new__(cls, *args, **kwargs):
		if not cls.__instance:
			cls.__instance = super(World, cls).__new__(cls, *args, **kwargs)
		return cls.__instance

	def __init__(self):
		self.teams = []
		self.listener = []
		#self.ants = []
		#self.sugars = [[0 for _ in xrange(WORLD_SIZE)] for _ in xrange(WORLD_SIZE)]
		self.entities = []

	def get_ants(self):
		return list(filter(lambda e: isant, self.entities))

	def get_sugars(self):
		return list(filter(lambda e: e.issugar and not e.isant, self.entities))

	def get_ants_for_team(self, teamid):
		return list(filter(lambda e: e.isant and e.tid == teamid, self.entities))

	def search_pos(self, x, y):
		return list(filter(lambda e: e.x==x and e.y==y, self.entities))

	'''
	Format of the 'hello' packet:
	Offset   Type      Description
	0        u16       client type (0=non-team, 1=team)
	2        16 chars  team name (if team client, else ignored)
	'''
	def login(self, loginstr):
		isplayer, teamname = struct.unpack('<Hs', loginstr)
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

		ant.world = self
		self.ants += ant

	def place_sugar(self, random=True, x=-1, y=-1):
		if random or x not in range(0,WORLD_SIZE) or y not in range(0,WORLD_SIZE):
			x = random.randint(0, WORLD_SIZE)
			y = random.randint(0, WORLD_SIZE)
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


'''
Each Object (6 bytes) is coded as follows:
Offset   Type    Description
0        u8      upper nibble: object type (0=empty, 1=ant, 2=sugar, 3=ant+sugar), lower nibble: team ID
1        u8      upper nibble: ant ID, lower nibble: ant health (1-10)
2        u16     horizontal (X) coordinate
4        u16     vertical (Y) coordinate
'''
class Entity(object):

	FMT_STR = '<BBHH'

	def __init__(self, world):
		self.world = world
		self.x = self.y = -1
		self.isant = self.issugar = False
		self.tid = self.antid = self.anthealth = -1

	def unpack(self, objstr):
		objinfo, antinfo, self.x, self.y = struct.unpack(Entity.FMT_STR, objstr)
		entitytype = objinfo >> 4
		self.isant = bool(entitytype % 2)
		self.issugar = bool((entitytype >> 1) % 2)
		self.tid = objinfo % (2 ** 4) if self.isant else -1
		self.antid = antinfo >> 4 if self.isant else -1
		self.anthealth = antinfo % (2 ** 4) if self.isant else -1

	def pack(self):
		return struct.pack(Entity.FMT_STR,
		                   int(self.isant) + int(self.issugar<<1) << 4 + self.tid,
		                   self.antid << 4 + self.anthealth,
		                   self.x, self.y)


class Ant(Entity):
	'''
		methods only to be used from the client
	'''

	def set_focus(self, x, y):
		''' specify a position and we will try to get there '''
		self.focus = (x,y)
		self.dir = Direction.NONE

	def move2focus(self):
		if dist_steps((self.x,self.y), self.focus) < 1:
			return
		self.dir = which_way(self.x, self.y, self.focus[0], self.focus[1])


def enum(**enums):
    return type('Enum', (), enums)

Direction = enum(
	NONE = 5,
	NW = 1,
	N = 2,
	NE = 3,
	E = 6,
	SE = 9,
	S = 8,
	SW = 7,
	W = 4
)


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

def which_way(x, y, goalX, goalY):
	if x < goalX and y < goalY: return Direction.SE
	if x < goalX and y > goalY: return Direction.NE
	if x > goalX and y < goalY: return Direction.SW
	if x > goalX and y > goalY: return Direction.NW
	if x < goalX: return Direction.E
	if x > goalX: return Direction.W
	if y < goalY: return Direction.N
	if y > goalY: return Direction.S
	return Direction.NONE
