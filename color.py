import pygame
import random
from random import shuffle
import math
import colorsys
from pygame.locals import *
from PIL import Image

WIDTH, HEIGHT = 512,512

running = 1

s_w, s_h = 0,0
p_count = 0

colors = []
colors_pos  = []
pixels = []

def setWH(w,h):
	global s_w, s_h, pixels, p_count
	s_w, s_h = w,h
	p_count = s_w*s_h
	pixels = [None]*s_w
	for x in range(0, s_w):
		for y in range(0, s_h):
			pixels[x] = [None]*s_h

def newColor(r,g,b):
	#if (r,g,b) in colors: 
	#	return False
	#else: 
		return True

# when using a photo
def setup():
	im = Image.open("test.png")
	rgb_im = im.convert('RGB')
	width, height = im.size
	setWH(width, height)
	i = 0
	j = 0
	while i < height:
		while j < width:
			r,g,b = rgb_im.getpixel((j, i))
			if not newColor(r,g,b):
				j += 1
				continue
			else:
				h,s,v = colorsys.rgb_to_hsv(r,g,b)
				colors.append((r,g,b,h,s,v))
				j += 1	
		print(i)
		i += 1
		j = 0
	sorted(colors, key=lambda color:color[3])
	#shuffle(colors)
	print(len(colors))

#with random colors
def createColors():
	global colors
	setWH(WIDTH, HEIGHT)
	i, j = 0,0
	while i < s_h:
		while j < s_w:
			r,g,b = random.randint(0,255), random.randint(0,255), random.randint(0,255)
			if not newColor(r,g,b):
				j += 1
				continue
			else:
				h,s,v = colorsys.rgb_to_hsv(r,g,b)
				colors.append((r,g,b,h,s,v))
				j += 1	
		print(i)
		i += 1
		j = 0
	colors = sorted(colors, key=lambda color:color[3], reverse=False)

def getNeighbours(pixel):
	x_from = -1
	y_from = -1
	x_to = 2
	y_to = 2
	if pixel[0] == 0:
		x_from = 0
	if pixel[0] == s_w-2:
		x_to = 0
	if pixel[1] == 0:
		y_from = 0
	if pixel[1] == s_h-2:
		y_to = 0

	n = []
	for x in range(x_from, x_to):
		for y in range(y_from, y_to):
			if not(x is 0 and y is 0):
				n.append( (pixels[pixel[0]+x][pixel[1]+y], (pixel[0]+x, pixel[1]+y)) )
	return n

def isBorderPixel(p):
	pixel = p[1]
	neighbours = getNeighbours(pixel)
	for n in neighbours:
		if n[0] is None:
			return True
	else:
		colors_pos.remove(p)
		return False

def freeSpace(pixel):
	free = []
	neighbours = getNeighbours(pixel)
	for n in neighbours:
		if(n[0] is None):
			free.append( (n[1][0], n[1][1]) )

	if(len(free) == 0):
		return (0,0)
	return random.choice(free)

# eucl. distance between two rgb colors
def distance(c1, c2):
	return (c1[0]-c2[0])*(c1[0]-c2[0]) + (c1[1]-c2[1])*(c1[1]-c2[1]) + (c1[2]-c2[2])*(c1[2]-c2[2])

# returns the best free spot based on the average distance to its neighbor colors
def average(color, pix):
	neighbours = getNeighbours(pix[1])	
	nnDist = 1000000
	bestPix = None
	for n in neighbours:
		if n[0] is None:
			newN = getNeighbours(n[1])
			count = 0
			dist = 0
			for nn in newN:
				if nn[0] is not None:
					dist = dist + distance(color, nn[0])
					count += 1
			if count == 0:
				avgDist = 0
			else:
				avgDist = dist/count
			if avgDist < nnDist:
				nnDist = avgDist
				bestPix = ((n[1][0],n[1][1]), avgDist)
	
	if bestPix is None:
		return ((0,0), 1000000)
	return bestPix

def findNeighbour(color):
	closest = 1000000
	result = None
	for pix in colors_pos:
		if isBorderPixel(pix):
			dist = distance(color, pix[0])
			if dist < closest:
				closest = dist
				result = pix
				if dist <= 3:
					return freeSpace(result[1])
	if(result == None):
		running = 0
		return (-1,-1)
	return freeSpace(result[1])

def findNeighbourAverage(color):
	closest = 1000000
	result = None
	for pix in colors_pos:
		if isBorderPixel(pix):
			temp = average(color, pix)
			if temp[1] < closest:
				closest = temp[1]
				result = temp
				if closest <= 3:
					return result[0]
	if(result == None):
		running = 0
		return (-1,-1)
	return result[0]


def placeColor(index):
	color = colors[index]
	if index == 0:
		return (int(s_w/2), int(s_h/2))
	else:
		return findNeighbour(color)

def placeColorAvg(index):
	global colors
	color = colors[index]
	if index == 0:
		return (int(s_w/2), int(s_h/2))
	else:
		return findNeighbourAverage(color)

#setup()
createColors()
pygame.init()
screen = pygame.display.set_mode((s_w, s_h))
screen.fill((255,255,255))

running = 1
index = 0
counter = 0
max = len(colors)
while running:
  for event in pygame.event.get():
    if event.type == QUIT:
      running = 0

  coord = placeColorAvg(index)
  screen.fill((colors[index][0],colors[index][1],colors[index][2]), Rect(coord[0],coord[1], 1, 1), 0) 
  colors_pos.append((colors[index], coord))
  pixels[coord[0]][coord[1]] = colors[index]
  
  if(index < max-1):
  	index += 1

  counter += 1
  frac = counter/p_count
  #print frac
  pygame.display.update()

pygame.quit()