import robot
import time

robot.left_distance.distance_mode = 1
robot.left_distance.start_ranging()
robot.right_distance.distance_mode = 1
robot.right_distance.start_ranging()

speed = 0.9


def speed_from_distance(distance):
    limited_distance = min(distance, 30) * speed
    return limited_distance / 30


try:
    robot.set_left(speed)
    robot.set_right(speed)

    while True:
        # do we have data:
        if robot.left_distance.data_ready and robot.right_distance.data_ready:
            left_dist = robot.left_distance.distance
            right_dist = robot.right_distance.distance
            l_speed = speed_from_distance(robot.right_distance.distance)
            r_speed = speed_from_distance(robot.left_distance.distance)
            print(
                "Left: {} cm R Sp: {}, Right: {} cm L Sp: {}".format(
                    left_dist, r_speed, right_dist, l_speed
                )
            )
            robot.set_left(l_speed)
            robot.set_right(r_speed)

            robot.left_distance.clear_interrupt()
            robot.right_distance.clear_interrupt()
            time.sleep(0.1)

finally:
    robot.stop()
    robot.left_distance.clear_interrupt()
    robot.right_distance.clear_interrupt()
    robot.left_distance.stop_ranging()
    robot.right_distance.stop_ranging()
