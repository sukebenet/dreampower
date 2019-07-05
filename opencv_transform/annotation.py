
#Object annotation class:
class BodyPart:
	
	def __init__(self, name, xmin, ymin, xmax, ymax, x, y, w, h):
		self.name = name
		#Bounding Box:
		self.xmin = xmin
		self.ymin = ymin
		self.xmax = xmax
		self.ymax = ymax
		#Center:
		self.x = x
		self.y = y
		#Dimensione:
		self.w = w
		self.h = h