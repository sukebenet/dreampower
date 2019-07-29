import numpy as np
import cv2
import os
import random

#My library:
from opencv_transform.annotation import BodyPart

###
#
#	maskdet_to_maskfin 
#	
#	steps:
#		1. Extract annotation
#			1.a: Filter by color
#			1.b: Find ellipses
#			1.c: Filter out ellipses by max size, and max total numbers
#			1.d: Detect Problems
#			1.e: Resolve the problems, or discard the transformation
#		2. With the body list, draw maskfin, using maskref
#
###

# create_maskfin ==============================================================================
# return:
#	(<Boolean> True/False), depending on the transformation process
def create_maskfin(maskref, maskdet, enable_pubes):
	
	#Create a total green image, in which draw details ellipses
	details = np.zeros((512,512,3), np.uint8)
	details[:,:,:] = (0,255,0)      # (B, G, R)

	#Extract body part features:
	bodypart_list = extractAnnotations(maskdet, enable_pubes);

	#Check if the list is not empty:
	if bodypart_list:
		
		#Draw body part in details image:
		for obj in bodypart_list:

			if obj.w < obj.h:
				aMax = int(obj.h/2) #asse maggiore
				aMin = int(obj.w/2) #asse minore
				angle = 0 #angle
			else:
				aMax = int(obj.w/2)
				aMin = int(obj.h/2)
				angle = 90

			x = int(obj.x)
			y = int(obj.y)

			#Draw ellipse
			if obj.name == "tit":
				cv2.ellipse(details,(x,y),(aMax,aMin),angle,0,360,(0,205,0),-1) #(0,0,0,50)
			elif obj.name == "aur":
				cv2.ellipse(details,(x,y),(aMax,aMin),angle,0,360,(0,0,255),-1) #red
			elif obj.name == "nip":
				cv2.ellipse(details,(x,y),(aMax,aMin),angle,0,360,(255,255,255),-1) #white
			elif obj.name == "belly":
				cv2.ellipse(details,(x,y),(aMax,aMin),angle,0,360,(255,0,255),-1) #purple
			elif obj.name == "vag":
				cv2.ellipse(details,(x,y),(aMax,aMin),angle,0,360,(255,0,0),-1) #blue
			elif obj.name == "hair":
				xmin = x - int(obj.w/2)
				ymin = y - int(obj.h/2)
				xmax = x + int(obj.w/2)
				ymax = y + int(obj.h/2)
				cv2.rectangle(details,(xmin,ymin),(xmax,ymax),(100,100,100),-1)

		#Define the green color filter
		f1 = np.asarray([0, 250, 0])   # green color filter
		f2 = np.asarray([10, 255, 10])
		
		#From maskref, extrapolate only the green mask		
		green_mask = cv2.bitwise_not(cv2.inRange(maskref, f1, f2)) #green is 0

		# Create an inverted mask
		green_mask_inv = cv2.bitwise_not(green_mask)

		# Cut maskref and detail image, using the green_mask & green_mask_inv
		res1 = cv2.bitwise_and(maskref, maskref, mask = green_mask)
		res2 = cv2.bitwise_and(details, details, mask = green_mask_inv)

		# Compone:
		maskfin = cv2.add(res1, res2)
		return maskfin
	
# extractAnnotations ==============================================================================
# input parameter:
# 	(<string> maskdet_img): relative path of the single maskdet image (es: testimg1/maskdet/1.png)
# return:
#	(<BodyPart []> bodypart_list) - for failure/error, return an empty list []
def extractAnnotations(maskdet, enable_pubes):

	#Load the image
	#image = cv2.imread(maskdet_img)

	#Find body part
	tits_list = findBodyPart(maskdet, "tit")
	aur_list = findBodyPart(maskdet, "aur")
	vag_list = findBodyPart(maskdet, "vag")
	belly_list = findBodyPart(maskdet, "belly")

	#Filter out parts basing on dimension (area and aspect ratio):
	aur_list = filterDimParts(aur_list, 100, 1000, 0.5, 3);
	tits_list = filterDimParts(tits_list, 1000, 60000, 0.2, 3);
	vag_list = filterDimParts(vag_list, 10, 1000, 0.2, 3);
	belly_list = filterDimParts(belly_list, 10, 1000, 0.2, 3);

	#Filter couple (if parts are > 2, choose only 2)
	aur_list = filterCouple(aur_list);
	tits_list = filterCouple(tits_list);

	#Detect a missing problem:
	missing_problem = detectTitAurMissingProblem(tits_list, aur_list) #return a Number (code of the problem)

	#Check if problem is SOLVEABLE:
	if (missing_problem in [3,6,7,8]):
		resolveTitAurMissingProblems(tits_list, aur_list, missing_problem)
	
	#Infer the nips:
	nip_list = inferNip(aur_list)

	#Infer the hair:
	hair_list = inferHair(vag_list, enable_pubes)

	#Return a combined list:
	return tits_list + aur_list + nip_list + vag_list + hair_list + belly_list

# findBodyPart ==============================================================================
# input parameters:
# 	(<RGB>image, <string>part_name)
# return
#	(<BodyPart[]>list)
def findBodyPart(image, part_name):

	bodypart_list = [] #empty BodyPart list

	#Get the correct color filter:
	if part_name == "tit":
		#Use combined color filter 
		f1 = np.asarray([0, 0, 0])   # tit color filter
		f2 = np.asarray([10, 10, 10])
		f3 = np.asarray([0, 0, 250])   # aur color filter
		f4 = np.asarray([0, 0, 255])
		color_mask1 = cv2.inRange(image, f1, f2)
		color_mask2 = cv2.inRange(image, f3, f4)
		color_mask = cv2.bitwise_or(color_mask1, color_mask2) #combine
	
	elif part_name == "aur":
		f1 = np.asarray([0, 0, 250])   # aur color filter
		f2 = np.asarray([0, 0, 255])
		color_mask = cv2.inRange(image, f1, f2)
	
	elif part_name == "vag":
		f1 = np.asarray([250, 0, 0])   # vag filter
		f2 = np.asarray([255, 0, 0])
		color_mask = cv2.inRange(image, f1, f2)

	elif part_name == "belly":
		f1 = np.asarray([250, 0, 250])   # belly filter
		f2 = np.asarray([255, 0, 255])
		color_mask = cv2.inRange(image, f1, f2)

	#find contours:
	contours, hierarchy = cv2.findContours(color_mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

	#for every contour:
	for cnt in contours:

		if len(cnt)>5: #at least 5 points to fit ellipse

			#(x, y), (MA, ma), angle = cv2.fitEllipse(cnt)
			ellipse = cv2.fitEllipse(cnt)

			#Fit Result:
			x = ellipse[0][0] #center x
			y = ellipse[0][1] #center y
			angle = ellipse[2] #angle
			aMin = ellipse[1][0]; #asse minore
			aMax = ellipse[1][1]; #asse maggiore

			#Detect direction:
			if angle == 0:
				h = aMax
				w = aMin
			else:
				h = aMin
				w = aMax
			
			#Normalize the belly size:
			if part_name == "belly":
				if w<15:
					w *= 2
				if h<15:
					h *= 2

			#Normalize the vag size:
			if part_name == "vag":
				if w<15:
					w *= 2
				if h<15:
					h *= 2

			#Calculate Bounding Box:
			xmin = int(x - (w/2))
			xmax = int(x + (w/2))
			ymin = int(y - (h/2))
			ymax = int(y + (h/2))

			bodypart_list.append(BodyPart(part_name, xmin, ymin, xmax, ymax, x, y, w, h ))

	return bodypart_list

# filterDimParts ==============================================================================
# input parameters:
# 	(<BodyPart[]>list, <num> minimum area of part,  <num> max area, <num> min aspect ratio, <num> max aspect ratio)
def filterDimParts(bp_list, min_area, max_area, min_ar, max_ar):

	b_filt = []

	for obj in bp_list:

		a = obj.w*obj.h #Object AREA
		
		if ((a > min_area)and(a < max_area)):

			ar = obj.w/obj.h #Object ASPECT RATIO

			if ((ar>min_ar)and(ar<max_ar)):

				b_filt.append(obj)

	return b_filt

# filterCouple ==============================================================================
# input parameters:
# 	(<BodyPart[]>list)
def filterCouple(bp_list):

	#Remove exceed parts
	if (len(bp_list)>2):

		#trovare coppia (a,b) che minimizza bp_list[a].y-bp_list[b].y
		min_a = 0
		min_b = 1
		min_diff = abs(bp_list[min_a].y-bp_list[min_b].y)
		
		for a in range(0,len(bp_list)):
			for b in range(0,len(bp_list)):
				#TODO: avoid repetition (1,0) (0,1)
				if a != b:
					diff = abs(bp_list[a].y-bp_list[b].y)
					if diff<min_diff:
						min_diff = diff
						min_a = a
						min_b = b
		b_filt = []

		b_filt.append(bp_list[min_a])
		b_filt.append(bp_list[min_b])

		return b_filt
	else:
		#No change
		return bp_list



# detectTitAurMissingProblem ==============================================================================
# input parameters:
# 	(<BodyPart[]> tits list, <BodyPart[]> aur list)
# return
#	(<num> problem code)
#   TIT  |  AUR  |  code |  SOLVE?  |
#    0   |   0   |   1   |    NO    |
#    0   |   1   |   2   |    NO    |
#    0   |   2   |   3   |    YES   |
#    1   |   0   |   4   |    NO    |
#    1   |   1   |   5   |    NO    |
#    1   |   2   |   6   |    YES   |
#    2   |   0   |   7   |    YES   |
#    2   |   1   |   8   |    YES   |
def detectTitAurMissingProblem(tits_list, aur_list):

	t_len = len(tits_list)
	a_len = len(aur_list)

	if (t_len == 0):
		if (a_len == 0):
			return 1
		elif (a_len == 1):
			return 2
		elif (a_len == 2):
			return 3
		else:
			return -1
	elif (t_len == 1):
		if (a_len == 0):
			return 4
		elif (a_len == 1):
			return 5
		elif (a_len == 2):
			return 6
		else:
			return -1
	elif (t_len == 2):
		if (a_len == 0):
			return 7
		elif (a_len == 1):
			return 8
		else:
			return -1
	else:
		return -1

# resolveTitAurMissingProblems ==============================================================================
# input parameters:
# 	(<BodyPart[]> tits list, <BodyPart[]> aur list, problem code)
# return
#	none
def resolveTitAurMissingProblems(tits_list, aur_list, problem_code):

	if problem_code == 3:

		random_tit_factor = random.randint(2, 5) #TOTEST

		#Add the first tit:
		new_w = aur_list[0].w * random_tit_factor #TOTEST
		new_x = aur_list[0].x
		new_y = aur_list[0].y

		xmin = int(new_x - (new_w/2))
		xmax = int(new_x + (new_w/2))
		ymin = int(new_y - (new_w/2))
		ymax = int(new_y + (new_w/2))

		tits_list.append(BodyPart("tit", xmin, ymin, xmax, ymax, new_x, new_y, new_w, new_w ))

		#Add the second tit:
		new_w = aur_list[1].w * random_tit_factor #TOTEST
		new_x = aur_list[1].x
		new_y = aur_list[1].y

		xmin = int(new_x - (new_w/2))
		xmax = int(new_x + (new_w/2))
		ymin = int(new_y - (new_w/2))
		ymax = int(new_y + (new_w/2))

		tits_list.append(BodyPart("tit", xmin, ymin, xmax, ymax, new_x, new_y, new_w, new_w ))

	elif problem_code == 6:

		#Find wich aur is full:
		d1 = abs(tits_list[0].x - aur_list[0].x)
		d2 = abs(tits_list[0].x - aur_list[1].x)

		if d1 > d2:
			#aur[0] is empty
			new_x = aur_list[0].x
			new_y = aur_list[0].y
		else:
			#aur[1] is empty
			new_x = aur_list[1].x
			new_y = aur_list[1].y

		#Calculate Bounding Box:
		xmin = int(new_x - (tits_list[0].w/2))
		xmax = int(new_x + (tits_list[0].w/2))
		ymin = int(new_y - (tits_list[0].w/2))
		ymax = int(new_y + (tits_list[0].w/2))

		tits_list.append(BodyPart("tit", xmin, ymin, xmax, ymax, new_x, new_y, tits_list[0].w, tits_list[0].w ))

	elif problem_code == 7:

		#Add the first aur:
		new_w = tits_list[0].w * random.uniform(0.03, 0.1) #TOTEST
		new_x = tits_list[0].x
		new_y = tits_list[0].y

		xmin = int(new_x - (new_w/2))
		xmax = int(new_x + (new_w/2))
		ymin = int(new_y - (new_w/2))
		ymax = int(new_y + (new_w/2))

		aur_list.append(BodyPart("aur", xmin, ymin, xmax, ymax, new_x, new_y, new_w, new_w ))

		#Add the second aur:
		new_w = tits_list[1].w * random.uniform(0.03, 0.1) #TOTEST
		new_x = tits_list[1].x
		new_y = tits_list[1].y

		xmin = int(new_x - (new_w/2))
		xmax = int(new_x + (new_w/2))
		ymin = int(new_y - (new_w/2))
		ymax = int(new_y + (new_w/2))
		
		aur_list.append(BodyPart("aur", xmin, ymin, xmax, ymax, new_x, new_y, new_w, new_w ))

	elif problem_code == 8:

		#Find wich tit is full:
		d1 = abs(aur_list[0].x - tits_list[0].x)
		d2 = abs(aur_list[0].x - tits_list[1].x)

		if d1 > d2:
			#tit[0] is empty
			new_x = tits_list[0].x
			new_y = tits_list[0].y
		else:
			#tit[1] is empty
			new_x = tits_list[1].x
			new_y = tits_list[1].y

		#Calculate Bounding Box:
		xmin = int(new_x - (aur_list[0].w/2))
		xmax = int(new_x + (aur_list[0].w/2))
		ymin = int(new_y - (aur_list[0].w/2))
		ymax = int(new_y + (aur_list[0].w/2))
		aur_list.append(BodyPart("aur", xmin, ymin, xmax, ymax, new_x, new_y, aur_list[0].w, aur_list[0].w ))

# detectTitAurPositionProblem ==============================================================================
# input parameters:
# 	(<BodyPart[]> tits list, <BodyPart[]> aur list)
# return
#	(<Boolean> True/False)
def detectTitAurPositionProblem(tits_list, aur_list):

	diffTitsX = abs(tits_list[0].x - tits_list[1].x)
	if diffTitsX < 40:
		print("diffTitsX")
		#Tits too narrow (orizontally)
		return True

	diffTitsY = abs(tits_list[0].y - tits_list[1].y)
	if diffTitsY > 120:
		#Tits too distanced (vertically)
		print("diffTitsY")
		return True

	diffTitsW = abs(tits_list[0].w - tits_list[1].w)
	if ((diffTitsW < 0.1)or(diffTitsW>60)):
		print("diffTitsW")
		#Tits too equals, or too different (width)
		return True

	#Check if body position is too low (face not covered by watermark)
	if aur_list[0].y > 350: #tits too low
		#Calculate the ratio between y and aurs distance
		rapp = aur_list[0].y/(abs(aur_list[0].x - aur_list[1].x))
		if rapp > 2.8:
			print("aurDown")
			return True

	return False

# inferNip ==============================================================================
# input parameters:
# 	(<BodyPart[]> aur list)
# return
#	(<BodyPart[]> nip list)
def inferNip(aur_list):
	nip_list = []

	for aur in aur_list:

		#Nip rules:
		# - circle (w == h)
		# - min dim: 5
		# - bigger if aur is bigger
		nip_dim = int(5 + aur.w*random.uniform(0.03, 0.09))

		#center:
		x = aur.x
		y = aur.y

		#Calculate Bounding Box:
		xmin = int(x - (nip_dim/2))
		xmax = int(x + (nip_dim/2))
		ymin = int(y - (nip_dim/2))
		ymax = int(y + (nip_dim/2))

		nip_list.append(BodyPart("nip", xmin, ymin, xmax, ymax, x, y, nip_dim, nip_dim ))

	return nip_list

# inferHair (TOTEST) ==============================================================================
# input parameters:
# 	(<BodyPart[]> vag list)
# return
#	(<BodyPart[]> hair list)
def inferHair(vag_list, enable):
	hair_list = []

	#70% of chanche to add hair
	if enable:

		for vag in vag_list:

			#Hair rules:
			hair_w = vag.w*random.uniform(0.4, 1.5)
			hair_h = vag.h*random.uniform(0.4, 1.5) 

			#center:
			x = vag.x
			y = vag.y - (hair_h/2) - (vag.h/2)

			#Calculate Bounding Box:
			xmin = int(x - (hair_w/2))
			xmax = int(x + (hair_w/2))
			ymin = int(y - (hair_h/2))
			ymax = int(y + (hair_h/2))

			hair_list.append(BodyPart("hair", xmin, ymin, xmax, ymax, x, y, hair_w, hair_h ))

	return hair_list
