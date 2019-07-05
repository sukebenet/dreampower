import sys
import cv2

from run import process

"""
main.py

 How to run:
 python3 main.py

"""

# ------------------------------------------------- main()
def main():

	#Read input image
	dress = cv2.imread("input.png")

	#Process
	watermark = process(dress)

	# Write output image
	cv2.imwrite("output.png", watermark)

	#Exit
	sys.exit()

if __name__ == '__main__':
	main()