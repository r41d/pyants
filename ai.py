#!/usr/bin/env python
# -*- coding: utf-8 *-*

from enum import Enum


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


def dist_steps((x1, y1), (x2, y2)):
	return max(abs(x1 - x2), abs(y1 - y2))


def which_way((x, y), (goalX, goalY)):
	if x < goalX and y < goalY: return Direction.SE
	if x < goalX and y > goalY: return Direction.NE
	if x > goalX and y < goalY: return Direction.SW
	if x > goalX and y > goalY: return Direction.NW
	if x < goalX: return Direction.E
	if x > goalX: return Direction.W
	if y < goalY: return Direction.S
	if y > goalY: return Direction.N
	return Direction.NONE


class AI(object):

	class Ant(object):
		def __init__(self, entity=None):  # Ant ctor gets passed an entity with teamID == clientID
			self.id = self.x = self.y = self.hp = -1
			self.from_entity(entity)
			self.focus = (500, 500)
			self.dir = Direction.NONE

		def from_entity(self, entity):
			self.id = entity.antid if entity else -1
			self.x = entity.x if entity else -1
			self.y = entity.y if entity else -1
			self.hp = entity.anthealth if entity else -1

		def isalive(self):
			return self.hp > 0
		alive = property(isalive)

		def set_focus(self, foc):
			self.focus = foc

		def move2focus(self):
			self.dir = which_way((self.x, self.y), self.focus)

	def __init__(self, client):
		self.id = client.tID
		self.world = client.world
		self.ants = [AI.Ant(None)] * 16

	def update_ants(self):
		own_ants = self.world.get_ants_for_team(self.id)
		for i in range(16):
			ant = filter(lambda e: e.antid == i, own_ants)
			assert len(ant) < 2
			self.ants[i].from_entity(ant[0])

	def get_my_ants(self):
		return self.world.get_ants_for_team(self.id)

	def find_nearest_sugar(self, ant):
		sugars = self.world.get_sugars()
		minSugar, minSteps = None, 1000

		for s in sugars:
			steps = dist_steps((ant.x, ant.y), (s.x, s.y))
			if steps < minSteps:
				minSugar = s
				minSteps = steps

		return minSugar  # None if no sugar in world

	def futtersuche(self):
		myants = self.get_my_ants()
		print 'client ID {} has {} ants'.format(self.id, len(myants))
		for a in self.ants:
			s = self.find_nearest_sugar(a)
			a.set_focus((s.x, s.y))
			a.move2focus()

	def calc_actions(self):
		return map(lambda a: a.dir, self.ants)
