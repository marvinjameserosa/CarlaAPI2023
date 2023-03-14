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

client.load_world('town05')
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

while vehicle.get_location().x < 15:
    move(1, 0)

print(vehicle.get_location().x)