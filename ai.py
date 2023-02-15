#!/usr/bin/env python
# -*- coding: utf-8 *-*

from enum import Enum
import inspect


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


def dist_steps(pos1, pos2):
	(x1, y1) = pos1
	(x2, y2) = pos2
	return max(abs(x1 - x2), abs(y1 - y2))


def which_way(pos, goal):
	(x, y) = pos
	(goalX, goalY) = goal
	if x < goalX and y < goalY: return Direction.SE
	if x < goalX and y > goalY: return Direction.NE
	if x > goalX and y < goalY: return Direction.SW
	if x > goalX and y > goalY: return Direction.NW
	if x < goalX: return Direction.E
	if x > goalX: return Direction.W
	if y < goalY: return Direction.S
	if y > goalY: return Direction.N
	return Direction.NONE


def turnaround(dir):
	if dir == Direction.NW: return Direction.SE
	if dir == Direction.N: return Direction.S
	if dir == Direction.NE: return Direction.SW
	if dir == Direction.E: return Direction.W
	if dir == Direction.SE: return Direction.NW
	if dir == Direction.S: return Direction.N
	if dir == Direction.SW: return Direction.NE
	if dir == Direction.W: return Direction.E


class AI(object):

	class Ant(object):
		def __init__(self, entity=None):  # Ant ctor gets passed an entity with teamID == clientID
			self.id = self.x = self.y = self.hp = -1
			self.hassugar = False
			self.from_entity(entity)
			self.focus = (500, 500)  # focus is 2-tuple, ALWAYS
			self.dir = Direction.NONE
			self.decided = False

		def from_entity(self, entity):
			if not entity: print('entity NONE')
			#else: print(entity.antid)
			self.id = entity.antid if entity else -1
			self.x = entity.x if entity else -1
			self.y = entity.y if entity else -1
			self.hp = entity.anthealth if entity else -1
			self.hassugar = entity.issugar if entity else False
			self.decided = False  # always False after receiving world data

		def isalive(self):
			return self.hp > 0
		alive = property(isalive)

		def move_toward_pos(self, foc):
			self.focus = foc
			self.dir = which_way((self.x, self.y), self.focus)

		def go_dir(self, dir):
			self.focus = None  # does this make sense?
			self.dir = (self.x, self.y)

		#def __str__(self):
		#	return 'A{}[{}×{};{}.{}]'.format(('+S' if self.hassugar else ''), self.x, self.y, self.id)

	def __init__(self, client):
		self.id = client.tID
		self.world = client.world
		self.ants = [AI.Ant(None) for _ in range(16)]  # 16 distinct references!!
		self.steps_taken = 0

	def update_ants(self):
		own_ants = self.world.get_ants_for_team(self.id)
		#print(map(str, own_ants))
		for i in range(16):
			ant = [e for e in own_ants if e.antid == i]
			#print(map(str, ant))
			assert len(ant) < 2
			self.ants[i].from_entity(ant[0] if len(ant) > 0 else None)

	@staticmethod
	def find_nearest(ant, entities):
		nearest_ent, min_steps = None, 1000

		for e in entities:
			steps = dist_steps((ant.x, ant.y), (e.x, e.y))
			if steps < min_steps:
				nearest_ent = e
				min_steps = steps

		return nearest_ent, min_steps  # nearest_ent = None if supplied entities were empty in world

	def find_nearest_sugar(self, ant):
		sugars = self.world.get_sugars()
		return self.find_nearest(ant, sugars)

	def find_nearest_enemy(self, ant):
		enemies = [a for a in self.world.get_ants() if a.tid != self.id]
		return self.find_nearest(ant, enemies)



	def perform_ai(self):
		if self.steps_taken < 20:
			self.start_formation()
		else:
			self.run_away_when_enemy_is_near()
			self.go_home_when_wounded()
			self.bring_sugar_home()
			self.is_in_base()
			self.search_sugar()
			self.move2middle()
		self.steps_taken += 1



	def run_away_when_enemy_is_near(self):
		for a in [a for a in self.ants if not a.decided]:
			(enemy, steps) = self.find_nearest_enemy(a)
			if steps < 5:
				print(inspect.stack()[0][3])
				a.dir = turnaround(which_way((a.x, a.y), (enemy.x, enemy.y)))
				a.decided = True


	def go_home_when_wounded(self):
		for a in [a for a in self.ants if not a.decided and a.hp < 5]:
			print(inspect.stack()[0][3])
			a.move_toward_pos(self.world.HOMEBASES[self.id].center)
			a.decided = True


	def bring_sugar_home(self):
		for a in [a for a in self.ants if not a.decided and a.hassugar]:
			print(inspect.stack()[0][3])
			if a.hassugar:
				base_bottom_left = self.world.HOMEBASES[self.id].center  # lauf mal in die mitte
				print('i think my base is at', base_bottom_left)
				a.move_toward_pos(base_bottom_left)
			a.decided = True


	def is_in_base(self):
		for a in [a for a in self.ants if not a.decided and self.world.HOMEBASES[self.id].collidepoint(a.x,a.y)]:
			print(inspect.stack()[0][3])
			a.dir = Direction.NE
			a.decided = True


	def search_sugar(self):
		for a in [a for a in self.ants if not a.decided and not a.hassugar]:
			print(inspect.stack()[0][3])
			(s, _) = self.find_nearest_sugar(a)
			if s:
				a.move_toward_pos((s.x, s.y))
			a.decided = True


	def start_formation(self):
		""" 0123
			4567		 N
			89AB		W★E
			CDEF		 S      """
		for a in [a for a in self.ants if not a.decided]:
			print(inspect.stack()[0][3])
			if a.id in [0xA, 0xF]: a.dir = Direction.SE
			if a.id in [  3,   7]: a.dir = Direction.NE
			if a.id in [0xC,   9]: a.dir = Direction.SW
			if a.id in [  0,   5]: a.dir = Direction.NW
			if a.id in [  1,   2]: a.dir = Direction.N
			if a.id in [  7, 0xB]: a.dir = Direction.E
			if a.id in [  4,   8]: a.dir = Direction.W
			if a.id in [0xD, 0xE]: a.dir = Direction.S


	def move2middle(self):
		for a in [a for a in self.ants if not a.decided]:
			print(inspect.stack()[0][3])
			a.move_toward_pos((500, 500))
			# don't change a.decided




	## not really AI, used to 'export' actions the ants want to perform
	def calc_actions(self):
		return [a.dir for a in self.ants]
