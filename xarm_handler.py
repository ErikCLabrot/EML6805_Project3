import serial
import math
import numpy as np
from lib.cartesian import compute_ik, compute_fk
from lib.inverse_kinematics import FREE_ANGLE

class xarmHandler(object):
	def __init__(self, serial, time):
		self.serial = serial
		self.time = time
		self.baud = 9600

	def move(self, point: tuple, time: int, hand_orientation=500, approach_angle=FREE_ANGLE, waypoints=1) -> None:
		if approach_angle != FREE_ANGLE:
			approach_angle = math.radians(approach_angle)
		t = compute_ik(point, hand_orientation, approach_angle)
		self.write(t)
		return t

	def write(self,angles):
		port = serial.Serial(self.serial,self.baud)
		#construct xarm message according to sdk
		header = 0x55
		cmd = 0x03
		param = bytearray([len(angles),self.time & 0xff, (self.time & 0xff00) >> 8])
		#print(param)
		for i in range(len(angles)):
			#print(i)
			position = angles[i]
			#position = math.degrees(position)
			#position = int((int(position) + 120) * 1000/240)
			#print(position)
			param.extend([len(angles)-i+1, position & 0xff, (position & 0xff00) >> 8])
			#print(param)

		length = len(param) + 2		
		#print([header,header,length,cmd])
		#print(param)
		port.write([header,header,length,cmd])
		port.write(param)
		port.close()

	def open_gripper(self):
		angle = 550
		time = 750
		port = serial.Serial(self.serial,self.baud)
		header = 0x55
		cmd = 0x03
		
		param = bytearray([0x01,time & 0xff, (time & 0xff00) >> 8])
		param.extend([0x01, angle & 0xff, (angle & 0xff00)>>8])
		length = len(param) + 2
		
		port.write([header,header,length,cmd])
		port.write(param)
		port.close

	def close_gripper(self):
		angle = 750
		time = 750
		port = serial.Serial(self.serial,self.baud)
		header = 0x55
		cmd = 0x03
		
		param = bytearray([0x01,time & 0xff, (time & 0xff00) >> 8])
		param.extend([0x01, angle & 0xff, (angle & 0xff00)>>8])
		length = len(param) + 2
		
		port.write([header,header,length,cmd])
		port.write(param)
		port.close
