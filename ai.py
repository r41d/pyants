#!/usr/bin/env python
# -*- coding: utf-8 *-*

import sys
from client import dist_steps, which_way
from objects import Direction

class AI(object):

	class Ant(object):
		def __init__(self, entity=None):  # Ant ctor gets passed an entity with teamID == clientID
			self.id = self.x = self.y = self.hp = -1
			self.from_entity(entity)
			self.focus = (500,500)
			self.dir = Direction.NONE

		def from_entity(self, entity):
			self.id = entity.antid if entity else -1
			self.x = entity.x if entity else -1
			self.y = entity.y if entity else -1
			self.hp = entity.anthealth if entity else -1

		def move2focus(self, foc):
			''' specify a position and we will try to get there '''
			self.focus = foc
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

		return minSugar  ## None if no sugar in world

	def futtersuche(self):
		myants = self.get_my_ants()
		print 'client ID {} has {} ants'.format(self.id, len(myants))
		for a in self.ants:
			s = self.find_nearest_sugar(a)
			a.move2focus((s.x, s.y))

	def calc_actions(self):
		return map(lambda a: a.dir, self.ants)
