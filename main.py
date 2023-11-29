import chess
import chess.engine
import stockfish
import serial
import numpy as np
import time
from xarm_handler import xarmHandler

def calculate_square_position(row,col):
	size = 26
	center = 0.5*size #cm
	r = row - 4
	c = col - 4

	x_chess = -(r*size - center)
	y_chess = (c*size - center)

	return x_chess,y_chess


def calculate_transform(chess_pos,z):
	base_to_board = 90
	board_edge = 18
	square_size = 26
	x_offset = square_size*4 + board_edge + base_to_board
	y_offset = 0
	z_offset = 10
	tf = np.array([[1,0,0,x_offset],
					[0,1,0,y_offset],
					[0,0,1,z_offset],
					[0,0,0,1]])

	point = np.array([chess_pos[0], chess_pos[1],z,1])

	point_tf = np.dot(tf,point)
	return point_tf

def calc_chess_move(move):
	#Swap rows and cols for 'transform'
	high = 100
	low = 30
	print("chess move got:")
	print(move)
	col1 = ord(move[0])-96
	row1 = int(move[1])
	col2 = ord(move[2])-96
	row2 = int(move[3])

	print(col1)
	print(row1)
	print(col2)
	print(row2)
	
	low1 = low - (8-col1)*2
	low2 = low - (8-col2)*2

	x,y = calculate_square_position(row1,col1)
	p1_h = calculate_transform((x,y),high)
	p1_l = calculate_transform((x,y),low1)

	x,y = calculate_square_position(row2,col2)
	p2_h = calculate_transform((x,y),high)
	p2_l = calculate_transform((x,y),low2)

	home = [100,0,100]
	return p1_h[0:3],p1_l[0:3],p2_h[0:3],p2_l[0:3],p2_h[0:3],home

def execute_chess_move(moves,delay,xarm):
	xarm.open_gripper()
	time.sleep(delay/1000)
	is_open = True

	for i in range(len(moves)):
		_ = xarm.move(moves[i],delay)
		time.sleep(delay/1000)
		if i == 1:
			xarm.close_gripper()
			is_open = True
			time.sleep(delay/1000)
		if i == (len(moves)-3):
			xarm.open_gripper()
			time.sleep(delay/1000)
			is_open = False

def main():
	#Configure Arduino Communication
	arduino_port = "COM4"
	arduino_baud = 9600
	arduino_com = serial.Serial(arduino_port, arduino_baud)

	#Configure Chessboard
	board = chess.Board()
	stockfish_path = "../stockfish/stockfish-windows-x86-64-avx2.exe"
	engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)

	#configure Arm
	com = "COM5"
	delay = 1500
	xarm = xarmHandler(com,delay)
	move = ""
	while not board.is_game_over():
		serial_data = arduino_com.readline().decode('utf-8').strip()
		print(serial_data)
		if serial_data != move:
			move += serial_data
		else:
			move = serial_data
		if len(move) == 4:
			#Get move from serial
			print("Move from arduino: ")
			print(move)
			uci_move = chess.Move.from_uci(move)
			print(uci_move)
			board.push(uci_move)
			engine_result = engine.play(board, chess.engine.Limit(time=1.0))
			engine_move = str(engine_result.move)
			print("Move from engine:")
			print(engine_move)

			# #Check if engine move is a capture
			if board.is_capture(chess.Move.from_uci(engine_move)):
			 	move = str(engine_move[2])
			 	move += str(engine_move[3]) + str('i') + str(9)
			 	move = calc_chess_move(move)
			 	execute_chess_move(move,delay,xarm)

			board.push(chess.Move.from_uci(engine_move))

			# #calculate square positions for moves
			moves = calc_chess_move(engine_move)
			execute_chess_move(moves,delay,xarm)
			move = ""
			arduino_com.flush()

if __name__ == "__main__":
	main()