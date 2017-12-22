import cv2
import numpy as np
import math
import random

img_dir = "imgs"

cv2.namedWindow( "image", cv2.WINDOW_NORMAL);
def showImage(img):
	cv2.imshow("image", np.hstack([img]))
	shape = img.shape
	width = shape[1]
	height = shape[0]
	cv2.resizeWindow('image', max(width + 5, 25), max(height + 5, 25))
	cv2.waitKey(1)

class Pipe():
	def __init__(self, rect, clear, pair):
		self.rect = rect
		self.emptyRect = clear
		self.pair = pair

		self.unmatched = True

class Bird():
	def __init__(self, rect, center, width, height):
		self.rect = rect
		self.center = center
		self.width = width
		self.height = height

class Enviornment():
	def __init__(self):
		self.bgSubtract = cv2.bgsegm.createBackgroundSubtractorMOG()
		self.pipes = []
		self.gameRect = None
		self.gameROI = None

	def update(self, img):
		self.latestImg = img

	def isGameOver(self):
		return self.match("gameover-1.png")

	def getGameRect(self, img):
		roi = cv2.selectROI(img, False)
		self.gameROI = roi
		self.gameRect = self.edgePoints(roi)

	def getBlanks(self):
		lower_bound = np.array([189, 142, 52], dtype="uint8")
		upper_bound = np.array([209, 152, 62], dtype="uint8")
		blueMask = cv2.inRange(self.latestImg, lower_bound, upper_bound)

		lower_bound = np.array([250, 250, 250], dtype="uint8")
		upper_bound = np.array([255, 255, 255], dtype="uint8")
		whiteMask = cv2.inRange(self.latestImg, lower_bound, upper_bound)

		blueScreen = cv2.bitwise_and(self.latestImg, self.latestImg, mask = blueMask)
		whiteScreen = cv2.bitwise_and(self.latestImg, self.latestImg, mask = whiteMask)
		screen = cv2.bitwise_or(blueScreen, whiteScreen)

		showImage(screen)

	def edgePoints(self, r):
		## ret (topLeft, topRight, bottomLeft, bottomRight)
		return [(r[0], r[1]), (r[0] + r[2], r[1]), (r[0], r[1] + r[3]), (r[0] + r[2], r[1] + r[3])]

	def intersects(self, r1, r2):
		e1 = self.edgePoints(r1)
		e2 = self.edgePoints(r2)

		if e1[0][0] > e2[3][0] or e2[0][0] > e1[3][0]:
			return False;

		if e1[0][1] > e2[3][1] or e2[0][1] > e1[3][1]:
			return False;

		return True;

	def getPipes(self):
		screen = self.bgSubtract.apply(self.latestImg)

		kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(20, 20))
		screen = cv2.morphologyEx(screen, cv2.MORPH_CLOSE, kernel)

		screen = cv2.GaussianBlur(screen, (9,9), 0)
		# screen = cv2.bilateralFilter(screen, 11, 25, 25)
		screen = cv2.Canny(screen, 20, 60)

		_, contours, heirarchy = cv2.findContours(screen, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

		imgHeight, _ = self.latestImg.shape[:2]

		# print("Allowing Ys > %f", (imgHeight - 68))

		pipeContours = []
		for contour in contours:
			rect = cv2.boundingRect(contour)
			area = cv2.contourArea(contour)
			# peri = cv2.arcLength(contour, True)
			edgePoints = self.edgePoints(rect)

			if ((edgePoints[0][1] > 50 and edgePoints[0][1] < 70) 
				or (edgePoints[2][1] > imgHeight - 80) and area > 500):
				pipeContours.append(rect)
				# print("Area: %f" % area)
				# cv2.drawContours(self.latestImg, [contour], -1, (0,255,0), 5)


		contours = pipeContours

		if len(contours) < 2:
			return

		pairs = dict()
		for i in range(0, len(contours)):
			contourA = contours[i]
			closestX = 1000000
			for j in range(0, len(contours)):
				if i != j:
					contourB = contours[j]

					dx = abs(contourA[0] - contourB[0])
					if dx < closestX and not self.intersects(contourA, contourB) and not contourA == contourB:
						closestX = dx
						match = j
			try: 
				pairs[i] = match
			except:
				## no match
				## only possible if there is only one unique contour
				return

		pipes = []
		for i in range(0, len(contours)):
			if pairs[pairs[i]] == i:
				if i > pairs[i]:
					# We already have this pair
					continue

				aRect = contours[i]
				bRect = contours[pairs[i]]

				if aRect[1] > bRect[1]:
					top = aRect
					bottom = bRect
				else:
					top = bRect
					bottom = aRect

				# Verify pipe pair
				dx = abs(aRect[0] - bRect[0])
				dy = bottom[1] - (top[1] + top[3])
				if dx < 10:
					eTop = self.edgePoints(top)
					eBottom = self.edgePoints(bottom)

					freeRect = (eBottom[2], eBottom[3], eTop[0], eTop[1])

					p1 = Pipe(eTop, freeRect, None)
					p2 = Pipe(eBottom, freeRect, p1)
					p1.pair = p2
					pipes.append(p2)
		# print ""
		# print ""
		return pipes

	def centerEdgePoints(self, center, width, height):
		topLeft = (center[0] - width/2, center[1] - height/2)
		topRight = (center[0] + width/2, center[1] - height/2)
		bottomLeft = (center[0] - width/2, center[1] + height/2)
		bottomRight = (center[0] + width/2, center[1] + height/2)

		return [topLeft, topRight, bottomLeft, bottomRight]


	def getBirdRect(self):
		lower_bound = np.array([77, 102, 232], dtype="uint8")
		upper_bound = np.array([90, 125, 255], dtype="uint8")
		orangeMask = cv2.inRange(self.latestImg, lower_bound, upper_bound)

		lower_bound = np.array([40, 188, 240], dtype="uint8")
		upper_bound = np.array([100, 250, 255], dtype="uint8")
		yellowMask = cv2.inRange(self.latestImg, lower_bound, upper_bound)

		orange_screen = cv2.bitwise_and(self.latestImg, self.latestImg, mask = orangeMask)
		yellow_screen = cv2.bitwise_and(self.latestImg, self.latestImg, mask = yellowMask)
		screen = cv2.bitwise_or(orange_screen, yellow_screen)

		screen = cv2.GaussianBlur(screen, (9,9), 0)
		kernel = np.ones((12,12),np.uint8)
		screen = cv2.dilate(screen, kernel)

		screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)

		_, screen = cv2.threshold(screen, 10, 255, cv2.THRESH_BINARY)
		
		screen = cv2.bilateralFilter(screen, 11, 25, 25)
		screen = cv2.Canny(screen, 20, 60)

		_, contours, heirarchy = cv2.findContours(screen, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		
		bird = None
		for contour in contours:
			area = cv2.contourArea(contour)
			if area > 1600 and area < 1800:
				## Found the bird. Get the rect
				peri = cv2.arcLength(contour, True)
				approx = cv2.approxPolyDP(contour, 0.05 * peri, True)
				rect = cv2.minAreaRect(approx)
				
				center = rect[0]
				width, height = rect[1]
				theta = rect[2]

				rect = self.centerEdgePoints(center, width, height)

				bird = Bird(rect, center, width, height)


		return bird



	def match(self, template, retAll = False):
		template = img_dir + "/" + template
		template = cv2.imread(template, cv2.IMREAD_UNCHANGED)
		
		screen = cv2.cvtColor(self.latestImg, cv2.COLOR_BGR2GRAY)
		template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

		r = cv2.matchTemplate(screen, template, cv2.TM_CCORR_NORMED)
		_, conf, minVal, maxVal = cv2.minMaxLoc(r)

		if (retAll):
			return conf, minVal, maxVal

		return conf == 1