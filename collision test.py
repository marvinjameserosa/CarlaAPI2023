import carla
import time
def on_collision(event):
    print("Collision detected!")
    vehicle.destroy()
    print("Vehicle Destroyed")

while True:
    try:
        client = carla.Client('localhost', 2000)
        client.set_timeout(10)  
        world = client.get_world()
        print("successfully connected")
        break
    except:
        print("Trying Again")


blueprints = world.get_blueprint_library()

vehicleBP = blueprints.find('vehicle.tesla.model3')
location = carla.Transform(carla.Location(x=-33, y=6, z=1), carla.Rotation(yaw=0))
vehicle = world.try_spawn_actor(vehicleBP, location)

vehicle.apply_control(carla.VehicleControl(throttle=1, steer=0))

colsensor_bp = blueprints.find('sensor.other.collision')
colsensor_transform = carla.Transform(carla.Location(x=1.0, z=1.0))
colsensor = None

try:
    colsensor = world.spawn_actor(colsensor_bp, colsensor_transform, attach_to=vehicle)
    colsensor.listen(lambda event: on_collision(event))
except Exception as e:
    print("Exception occurred:", e)

# Sleep the main thread so the program doesn't exit immediately
while True:
    time.sleep(1)
