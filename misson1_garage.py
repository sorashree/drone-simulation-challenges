from pysimverse import Drone
import time

drone=Drone()
drone.connect()
drone.take_off()

drone.move_forward(50)
drone.move_left(250)
drone.move_forward(100)
drone.move_right(260)
drone.move_forward(200)
drone.move_right(270)

drone.land()
time.sleep(1)