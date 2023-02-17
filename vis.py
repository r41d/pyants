#!/usr/bin/env python
# -*- coding: utf-8 *-*

import sys
import string
from enum import Enum
import pygame
from client import AntClient
from objects import World  #, Team, Entity


class Vis(object):
	size = width, height = 1000 + 380, 1000
	FPS = 60

	class Colors(Enum):
		black = (  0,   0,   0)
		white = (255, 255, 255)
		grey  = (127, 127, 127)
		red   = (255,   0,   0)
		green = (  0, 255,   0)
		blue  = (  0,   0, 255)

	teamColors = [(0, 110, 110), (240, 0, 0), (0, 240, 0), (160, 0, 80),
	              (200, 40, 0), (0, 200, 40), (40, 0, 200), (160, 80, 0),
	              (0, 160, 80), (80, 0, 160), (120, 120, 0), (0, 120, 120),
	              (120, 0, 120), (80, 160, 0), (0, 80, 160), (240, 0, 0)
	]

	@staticmethod
	def draw_text(disp, text, font, pos, color):
		label = font.render(text, 1, color)
		posi = label.get_rect(topleft=(pos[0], pos[1]))
		disp.blit(label, posi)

	@staticmethod
	def draw_cross(disp, x, y, color, diag=False, leng=5):
		if not diag:
			pygame.draw.line(disp, color, (x - leng, y), (x + leng, y))
			pygame.draw.line(disp, color, (x, y - leng), (x, y + leng))
		else:
			pygame.draw.line(disp, color, (x - leng, y - leng), (x + leng, y + leng))
			pygame.draw.line(disp, color, (x - leng, y + leng), (x + leng, y - leng))

	def __init__(self, client):
		if len(sys.argv) < 2:
			print('Usage: ' + sys.argv[0] + ' host')
			exit(1)

		pygame.init()
		self.font = pygame.font.Font('LiberationMono-Regular.ttf', 18)

		pygame.display.set_caption('Ant!')
		self.DISPLAY = pygame.display.set_mode(self.size)
		self.HomeBaseSurface = pygame.Surface((1001,1000))
		for (c, b) in zip(range(16), World.HOMEBASES):
			pygame.draw.rect(self.HomeBaseSurface, self.teamColors[c], (b.x, b.y, 20, 20))
		pygame.draw.line(self.HomeBaseSurface, self.Colors.white.value, (1000, 0), (1000, 999))

		self.TIMER = pygame.time.Clock()

		self.client = client

	def update(self):
		#self.client.update_world() ### now done outside
		world = self.client.world

		if pygame.event.peek(pygame.QUIT):
			sys.exit()
		pygame.event.clear()

		self.DISPLAY.fill(Vis.Colors.black.value)
		self.DISPLAY.blit(self.HomeBaseSurface, (0, 0))

		for e in world.entities:
			#if e.isant:
			#	ANT.rect.center = (e.x, e.y)
			#	grp.draw(DISPLAY)
			#else:
			if e.isant and not e.issugar:
				self.draw_cross(self.DISPLAY, e.x, e.y, Vis.teamColors[e.tid], False, 5)
			elif not e.isant and e.issugar:
				#draw_cross(DISPLAY, e.x, e.y, white, True, 2)
				self.DISPLAY.set_at((e.x, e.y), Vis.Colors.white.value)
			elif e.isant and e.issugar:
				self.draw_cross(self.DISPLAY, e.x, e.y, Vis.teamColors[e.tid], True, 4)
			else:
				#print 'object is neither ant nor sugar!!!'
				pass
			#DISPLAY.set_at((e.x, e.y), color)

		self.draw_text(self.DISPLAY, 'ID Ants Score Name', self.font, (1020, 50), Vis.Colors.white.value)
		for t in world.teams:
			name = ''.join([chr(c) for c in t.name if chr(c) in string.printable])
			self.draw_text(self.DISPLAY,
			          '{:>2}   {:>2} {:>5} {}'.format(t.id, t.ants, t.sugar, name),
			          self.font, (1020, 80 + t.id * 20), Vis.teamColors[t.id])

		self.TIMER.tick(self.FPS)
		pygame.display.update()


if __name__ == '__main__':
	client = AntClient(sys.argv[1], False, 'spectator^^')  # here happens the network stuff in the AntClient ctor
	vis = Vis(client)
	while True:
		client.update_world()
		vis.update()
