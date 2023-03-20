import carla
import cv2
import math
import numpy as np

run  = True
speed = 0
obstacle_distance = None

IP_ADDRESS = 'localhost'
PORT = 2000
TIMEOUT = 50
TOWN = 'Town05'
EGO_VEHICLE = 'vehicle.tesla.model3'

while True:
    try:
        client = carla.Client(IP_ADDRESS, PORT)
        client.set_timeout(TIMEOUT)
        world = client.get_world()
        print("Successfully Connected to Client!")
        break
    except:
        print("Trying Again...")

blueprints = world.get_blueprint_library()
spawn_points = world.get_map().get_spawn_points()

# Ego Vehicle
ego_vehicle_bp = blueprints.find(EGO_VEHICLE)
location = carla.Transform(carla.Location(x=30, y=6, z=1), carla.Rotation(yaw=0))
ego_vehicle = world.try_spawn_actor(ego_vehicle_bp, location)

# Obstacle Detector
obstacle_bp = blueprints.find('sensor.other.obstacle')
obstacle_transform = carla.Transform(carla.Location(x=6.0, z=1.0))
try:
    obstacle_sensor = world.spawn_actor(obstacle_bp, obstacle_transform, attach_to=ego_vehicle)
    obstacle_sensor.listen(lambda event: Obstacle_Distance(event))
except:
    pass

# Collision Sensor
colsensor_bp = blueprints.find('sensor.other.collision')
colsensor_transform = carla.Transform(carla.Location(x=1.0, z=1.0))
try:
    colsensor = world.spawn_actor(colsensor_bp, colsensor_transform, attach_to=ego_vehicle)
    #colsensor.listen(lambda event: on_collision(event))
except:
    pass

def Despawn_All_Vehicles():
    actor_list = world.get_actors()
    for actor in actor_list:
        if 'vehicle' in actor.type_id:
            actor.destroy()
            print("Vehicle Deleted")

def LoadTown():
    client.load_world(TOWN)
    print("Town Loaded")

def Ego_Movement(): 
    ego_vehicle.apply_control(carla.VehicleControl(throttle=1, steer=0, brake=0))

def Speed_Limit(): 
    global speed
    #print(speed)
    if speed > 30:
        ego_vehicle.apply_control(carla.VehicleControl(brake=1)) 

def Speedometer():
    global speed 
    speed = 0
    velocity = ego_vehicle.get_velocity()
    speed = 3.6 * (velocity.x**2 + velocity.y**2 + velocity.z**2)**0.5
    #print(self.speed, "km/h")

def Auto_Brake():
    global obstacle_distance 
    global speed
    if not obstacle_distance == None:
        print(speed)
        ego_vehicle.apply_control(carla.VehicleControl(brake=1))
        


def Obstacle_Distance(event):
    global obstacle_distance
    obstacle_location = event.other_actor.get_location()
    vehicle_location = ego_vehicle.get_location()
    obstacle_distance = math.sqrt(((obstacle_location.x - vehicle_location.x)**2) + ((obstacle_location.y - vehicle_location.y)**2) + ((obstacle_location.z - vehicle_location.z)**2))
    print("Obstacle detected at distance: ", obstacle_distance)

def on_collision(event):
    global run
    run = False
    collision = event.other_actor
    print("Vehicle collided with", collision.type_id)
    ego_vehicle.destroy()
    



def Update():
    global run
    run = True
    while run:
        try:
            world.tick()
            Ego_Movement()
            Speedometer()
            Speed_Limit()
            Auto_Brake()
        except:
            pass


if __name__ == "__main__":
    Update()
    #LoadTown()
    #Despawn_All_Vehicles()
