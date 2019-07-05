import numpy as np
import cv2
import os

###
#
#	maskdet_to_maskfin 
#	
#
###

# create_maskref ===============================================================
# return:
#	maskref image
def create_maskref(cv_mask, cv_correct):

	#Create a total green image
	green = np.zeros((512,512,3), np.uint8)
	green[:,:,:] = (0,255,0)      # (B, G, R)

	#Define the green color filter
	f1 = np.asarray([0, 250, 0])   # green color filter
	f2 = np.asarray([10, 255, 10])
	
	#From mask, extrapolate only the green mask		
	green_mask = cv2.inRange(cv_mask, f1, f2) #green is 0

	# (OPTIONAL) Apply dilate and open to mask
	kernel = np.ones((5,5),np.uint8) #Try change it?
	green_mask = cv2.dilate(green_mask, kernel, iterations = 1)
	#green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_OPEN, kernel)

	# Create an inverted mask
	green_mask_inv = cv2.bitwise_not(green_mask)

	# Cut correct and green image, using the green_mask & green_mask_inv
	res1 = cv2.bitwise_and(cv_correct, cv_correct, mask = green_mask_inv)
	res2 = cv2.bitwise_and(green, green, mask = green_mask)

	# Compone:
	return cv2.add(res1, res2)