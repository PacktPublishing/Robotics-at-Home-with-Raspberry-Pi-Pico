import robot
import time

robot.left_distance.distance_mode = 1
robot.right_distance.distance_mode = 1

too_close_cm = 30
speed = 0.9

robot.left_distance.start_ranging()
robot.right_distance.start_ranging()

try:
    robot.set_left(speed)
    robot.set_right(speed)

    while True:
        # do we have data:
        if robot.left_distance.data_ready and robot.right_distance.data_ready:
            left_dist = robot.left_distance.distance
            right_dist = robot.right_distance.distance
            # are any too close
            if right_dist < too_close_cm:
                print(
                    "Obstacle detected - Left: {} cm, Right: {} cm".format(
                        left_dist, right_dist
                    )
                )
                robot.set_left(-speed)
            else:
                robot.set_left(speed)
                if left_dist < too_close_cm:
                    print(
                        "Obstacle detected - Left: {} cm, Right: {} cm".format(
                            left_dist, right_dist
                        )
                    )
                    robot.set_right(-speed)
                else:
                    robot.set_right(speed)

            robot.left_distance.clear_interrupt()
            robot.right_distance.clear_interrupt()
            time.sleep(0.1)

finally:
    robot.stop()
    robot.left_distance.clear_interrupt()
    robot.right_distance.clear_interrupt()
    robot.left_distance.stop_ranging()
    robot.right_distance.stop_ranging()
