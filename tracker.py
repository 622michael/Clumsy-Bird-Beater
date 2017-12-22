from kvb import Pipe
import random
import copy
import math

class ObjectTracker:
	def __init__(self):
		self.numBirds = 0
		self.bird = None

		self.pipes = []
		self.numPipes = 0

	def foundBird(self, newBird):
		if self.bird is None:
			self.bird = newBird
		else:
			dY = abs(self.bird.center[1] - newBird.center[1])
			dX = abs(self.bird.center[0] - newBird.center[0])

			if dX > 50:
				if self.numBirds < 2:
					return False
				else:
					return False
			else:
				self.bird = newBird
				return True

	def matches(self, objects1, objects2, similarity):
		matches = dict()
		for i in range(0, len(objects1)):
			o1 = objects1[i]

			best = 10000
			match = None
			for j in range(0, len(objects2)): 
				o2 = objects2[j]

				value = similarity(o1, o2)
				if value < best:
					match = j
					best = value

			matches[i] = match

		return matches

	def pipeIsRelavent(self, pipe):
		return pipe.emptyRect[3][0] > self.bird.center[0]

	def incrementX(self, rect, dX):
		r = ()
		for point in rect:
			r += ((point[0] + dX, point[1]), )
		return r

	def movePipe(self, pipe, dX, follow = True):
		rect = self.incrementX(pipe.rect, dX)
		emptyRect = self.incrementX(pipe.emptyRect, dX)

		if follow: 
			pair = self.movePipe(pipe.pair, dX, follow = False)
		else:
			pair = pipe.pair

		return Pipe(rect, emptyRect, pair)

	def distance(self, p1, p2):
		return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) 


	def foundPipes(self, newPipes):
		if (self.bird is None):
			return
		
		f = lambda o1, o2 : self.distance(o1.rect[0], o2.rect[0])
		
		unmatchedNewPipes = copy.copy(newPipes)
		oldPipes = []

		unmatchedPipes = []

		if (len(newPipes) != 0 and len(self.pipes) != 0):
	
			matches = self.matches(self.pipes, newPipes, f)
			newMatches = self.matches(newPipes, self.pipes, f)

			totaldX = 0
			numMatches = 0

			for i in matches:
				match = matches[i]
				if match is not None:
					if newMatches[match] == i:
						newPipe = newPipes[match]
						pipe = self.pipes[i]

						dX = newPipe.emptyRect[0][0] - pipe.emptyRect[0][0] 
						totaldX += dX
						numMatches += 1

						unmatchedNewPipes.remove(newPipe)

						if (self.pipeIsRelavent(newPipe)):
							newPipe.color = self.pipes[i].color
							newPipe.unmatched = False
							self.pipes[i] = newPipe
						else:
							oldPipes.append(self.pipes[i])
					else:
						if (self.pipeIsRelavent(self.pipes[i])):
							unmatchedPipes.append(i)
						else:
							oldPipes.append(self.pipes[i])
				else:
					## No objects in newPipes
					print "objects in newPipes: %i" % len(newPipes)

			if numMatches != 0: 
				average_dX = totaldX/numMatches
			else:
				average_dX = 0
		else:
			unmatchedPipes = range(0, len(self.pipes))
			average_dX = 0

		for i in unmatchedPipes:
			pipe = self.pipes[i]
			if pipe.unmatched:
				## The pipe hasn't been matched in
				## two frames.
				oldPipes.append(self.pipes[i])
			else:
				## Assume it failed to be detected
				## increment based on avg dX
				pipe = self.pipes[i]
				newPipe = self.movePipe(pipe, average_dX)
				newPipe.color = pipe.color

				if self.pipeIsRelavent(newPipe):
					newPipe.unmatched = True
					self.pipes[i] = newPipe
				else:
					oldPipes.append(self.pipes[i])


		for newPipe in unmatchedNewPipes:
			newPipe.color = (random.randrange(255), random.randrange(255), random.randrange(255))
			self.pipes.append(newPipe)

		for pipe in oldPipes:
			print "Removing %s" % (pipe.emptyRect[:4], )
			self.pipes.remove(pipe)

		return self.pipes


