import carla
import time
import math
while True:
        try:
            client = carla.Client('localhost', 2000)
            client.set_timeout(10)
            world = client.get_world()
            print("successfully connected")
            break
        except:
            print("Trying Again")

### To Get Blueprint
blueprints = world.get_blueprint_library()

### To Get SpawnPoints
spawnpoints = world.get_map().get_spawn_points()

### To Get Spectator
spectator = world.get_spectator()

# Spawn a vehicle
vehicleBP = blueprints.find('vehicle.tesla.model3')
location = carla.Transform(carla.Location(x=-33, y=6, z=1), carla.Rotation(yaw=0))
vehicle = world.try_spawn_actor(vehicleBP, location)




def move(x, y):
     vehicle.apply_control(carla.VehicleControl(throttle=x, steer=y))

def breaking(x):
     control = carla.VehicleControl(brake=x)
     vehicle.apply_control(control)

while vehicle.get_location().x < 15:
    move(0.5, 0)
breaking(1)
time.sleep(2.5)
while not vehicle.get_transform().rotation.yaw >= 80:
    move(0.5,1)
breaking(1)
time.sleep(2.5)
while vehicle.get_location().y < 74:
    move(0.5, 0)
breaking(1)
time.sleep(3)
print(vehicle.get_transform().rotation.yaw) 
while not vehicle.get_transform().rotation.yaw >= 180:
    move(0.5,1)

breaking(1)

time.sleep(5)
print(vehicle.get_transform().rotation.yaw)
vehicle.destroy()