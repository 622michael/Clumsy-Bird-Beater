from kvb import Enviornment
from kvb import showImage
from kvb import Bird
from kvb import Pipe
import cv2
import os
import glob
import timeit
import time
import random
from tracker import ObjectTracker
from camera import Camera
import numpy as np

e = Enviornment()

cameraDir = "tmp/camera"

# f = "imgs/clumsy.png"
# img = cv2.imread(f)
# showImage(img)
# cv2.colormap(colorMap)

def drawRect(img, r, color = (255,255,0), thickness = 5):
	cv2.rectangle(img, (int(r[0][0]), int(r[0][1])), (int(r[3][0]), int(r[3][1])), color, thickness)

e = Enviornment()

tracker = ObjectTracker()

camera = Camera()

while True:
	img = camera.record()
	

# img = camera.snapshot()
# e.getGameRect(img)



# path = os.path.join(cameraDir, '*.png')
# files = sorted(glob.glob(path), key=os.path.getmtime)

# # totalTime = 0
# # num = 0

# # birdColor = (255,255,0)

# for f in files:
# 	img = cv2.imread(f)
	e.update(img)

	# e.getPipes()

	if e.isGameOver():
		print("Game over")
	else:
		bird = e.getBirdRect()
		
		if bird is not None:
			tracker.foundBird(bird)

	pipes = e.getPipes()

	if pipes is not None:
		tracker.foundPipes(pipes)
		for pipe in tracker.pipes:
			drawRect(img, pipe.rect, color = pipe.color)
			drawRect(img, pipe.pair.rect, color = pipe.color)
			drawRect(img, pipe.emptyRect, color = pipe.color)
	else:
		tracker.foundPipes([])

	if tracker.bird is not None:
		drawRect(img, tracker.bird.rect)

	showImage(img)
