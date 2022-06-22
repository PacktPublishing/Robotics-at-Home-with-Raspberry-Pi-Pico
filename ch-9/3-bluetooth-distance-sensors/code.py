import board 
import time
import busio
import robot

uart = busio.UART(board.GP12,board.GP13,baudrate=9600, timeout=0.01)

print("Initialising sensors")
robot.left_distance.distance_mode = 1
robot.left_distance.start_ranging()
robot.right_distance.distance_mode = 1
robot.right_distance.start_ranging()

print("Sending via UART...")
while True:
    if robot.left_distance.data_ready and robot.right_distance.data_ready:
        sensor1 = robot.left_distance.distance
        sensor2 = robot.right_distance.distance
        try:
            sensor_packet = f"{sensor1},{sensor2},10,15,49.23,-3\n"
            print(sensor_packet, end='')
            uart.write(sensor_packet.encode('utf-8'))
        finally:
            robot.left_distance.clear_interrupt()
            robot.right_distance.clear_interrupt()
    time.sleep(0.05)

# installinig the bluetooth update ovre the air makes it work better with
# floating point, 6 channels, negatives all confirmed.