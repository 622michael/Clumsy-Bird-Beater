import os
import cv2
import time
import datetime
from mss import mss
from PIL import Image
from PIL import ImageGrab
import numpy

tmp_storage_dir = "tmp/camera/"

class Camera:
	def __init__(self):
		self.date = datetime.datetime.now()
		self.storage_dir = tmp_storage_dir + self.date.strftime("%H%M%S%d%Y")
		self.imageSize = (640, 400)
		self.screen = mss()
		self.latestImage = None

		try:
			os.system(self.storage_dir)
		except OSError:
			# The folder exists
			pass

		self.index = 0


	def snapshot(self):
		snapshot_path = self.storage_dir + "SNAPSHOT%i" % self.index + ".png"
		os.system("screencapture " + snapshot_path)

		self.index = self.index + 1

		bigSnapshot = cv2.imread(snapshot_path)
		width, height, _ = bigSnapshot.shape
		resized = cv2.resize(bigSnapshot, self.imageSize)
		return resized

	def record(self):
		img = ImageGrab.grab()
		self.latestImage = numpy.array(img) 
		self.latestImage = cv2.cvtColor(self.latestImage, cv2.COLOR_RGB2BGR)
		self.latestImage = cv2.resize(self.latestImage, self.imageSize)
		# # Convert RGB to BGR 
		# self.latestImage = open_cv_image[:, :, ::-1].copy() 
		return self.latestImage


	def clearMemory(self):
		pass


# c = Camera()
# while (True):
# 	c.snapshot()

# 	time.sleep(0.1)