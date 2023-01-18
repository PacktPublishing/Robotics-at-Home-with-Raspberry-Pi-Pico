import board 
import time
import busio
import robot

uart = busio.UART(board.GP12, board.GP13, baudrate=9600)

robot.left_distance.distance_mode = 1
robot.left_distance.start_ranging()
robot.right_distance.distance_mode = 1
robot.right_distance.start_ranging()

while True:
    if robot.left_distance.data_ready and robot.right_distance.data_ready:
        sensor1 = robot.left_distance.distance
        sensor2 = robot.right_distance.distance
        uart.write(f"{sensor1},{sensor2}\n".encode())
        robot.left_distance.clear_interrupt()
        robot.right_distance.clear_interrupt()
    time.sleep(0.05)
