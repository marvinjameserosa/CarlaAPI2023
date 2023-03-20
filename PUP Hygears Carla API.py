import carla
import cv2
import math
import numpy as np


IP_ADDRESS = 'localhost'
PORT = 2000
TIMEOUT = 50
TOWN = 'Town05'
EGO_VEHICLE = 'vehicle.tesla.model3'
image_count = 0
class Carla():

    def __init__(self):
        while True:
            try:
                self.client = carla.Client(IP_ADDRESS, PORT)
                self.client.set_timeout(TIMEOUT)
                self.world = self.client.get_world()
                print("Successfully Connected to Client!")
                break
            except:
                print("Trying Again...")

        self.blueprints = self.world.get_blueprint_library()
        self.spawn_points = self.world.get_map().get_spawn_points()

        # Ego Vehicle
        ego_vehicle_bp = self.blueprints.find(EGO_VEHICLE)
        location = carla.Transform(carla.Location(x=30, y=6, z=1), carla.Rotation(yaw=0))
        self.ego_vehicle = self.world.try_spawn_actor(ego_vehicle_bp, location)
        self.Collision_Sensors()
        self.RGB_Cam_Sensors()
        self.Take_Pictures()
        self.Obstacle_Sensors()

        # Game Loop
        self.run = True

        # Input
        self.raw_image = None
        self.collide = False
        self.obstacle_distance = None
        self.speed = None
        
        # Output
        self.throttle = 1
        self.steer = 0
        self.breaking = 0

    def LoadTown(self):
        town = self.client.load_world(TOWN)
        print("Town Loaded")
    
    def Reset(self):
        self.LoadTown()
        self.blueprints = self.world.get_blueprint_library()
        self.spawn_points = self.world.get_map().get_spawn_points()

        # Ego Vehicle
        ego_vehicle_bp = self.blueprints.find(EGO_VEHICLE)
        location = carla.Transform(carla.Location(x=30, y=6, z=1), carla.Rotation(yaw=0))
        self.ego_vehicle = self.world.try_spawn_actor(ego_vehicle_bp, location)
        self.Collision_Sensors()
        self.RGB_Cam_Sensors()
        self.Take_Pictures()
        self.Obstacle_Sensors()

        # Game Loop
        self.run = True

        # Input
        self.raw_image = None
        self.collide = False
        self.obstacle_distance = None
        self.speed = None
        
        # Output
        self.throttle = 1
        self.steer = 0
        self.breaking = 0
    
    def Despawn_All_Vehicles(self):
        actor_list = self.world.get_actors()
        for actor in actor_list:
            if 'vehicle' in actor.type_id:
                actor.destroy()
                print("Vehicle Deleted")

    def Ego_Movement(self): 
        self.ego_vehicle.apply_control(carla.VehicleControl(throttle=self.throttle, steer=self.steer, brake=self.breaking))

    def Speed_Limit(self): 
        if self.speed > 35:
            self.ego_vehicle.apply_control(carla.VehicleControl(brake=1)) 

    def Speedometer(self):
        velocity = self.ego_vehicle.get_velocity()
        self.speed = 3.6 * (velocity.x**2 + velocity.y**2 + velocity.z**2)**0.5
        #print(self.speed, "km/h")

    def RGB_Cam_Sensors(self):
        camera_bp = self.blueprints.find('sensor.camera.rgb')
        camera_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
        self.camera = self.world.spawn_actor(camera_bp, camera_transform, attach_to=self.ego_vehicle)

    def Process_Image(self, image):
        image.convert(carla.ColorConverter.Raw)
        self.raw_image = np.array(image.raw_data)
        self.raw_image = self.raw_image.reshape((image.height, image.width, 4))
        self.raw_image = self.raw_image[:, :, :3]
        #cv2.imshow("Camera View", self.raw_image)
        #cv2.waitKey(1)

    def Take_Pictures(self):
        self.camera.listen(lambda image: self.Process_Image(image))
    

    def on_collision(self, event, _):
        collision = event.other_actor
        print("Vehicle collided with", collision.type_id)
        self.ego_vehicle.destroy()
        self.collide = True
        self.run = False

    def Collision_Sensors(self):
        colsensor_bp = self.blueprints.find('sensor.other.collision')
        colsensor_transform = carla.Transform(carla.Location(x=1.0, z=1.0))
        try:
            self.colsensor = self.world.spawn_actor(colsensor_bp, colsensor_transform, attach_to=self.ego_vehicle)
            self.colsensor.listen(lambda event: self.on_collision(event, self))
        except Exception as e:
            print("Exception occurred:", e)
    

    def Obstacle_Sensors(self):
        obstacle_bp = self.blueprints.find('sensor.other.obstacle')
        obstacle_transform = carla.Transform(carla.Location(x=2.0, z=1.0))
        try:
            self.obstacle_sensor = self.world.spawn_actor(obstacle_bp, obstacle_transform, attach_to=self.ego_vehicle)
            self.obstacle_sensor.listen(lambda event: self.Obstacle_Distance(event, self))
        except Exception as e:
            print("Exception occurred:", e)
    
    def Obstacle_Distance(self, event, _):
        obstacle_location = event.other_actor.get_location()
        vehicle_location = self.ego_vehicle.get_location()
        self.obstacle_distance = math.sqrt(((obstacle_location.x - vehicle_location.x)**2) + ((obstacle_location.y - vehicle_location.y)**2) + ((obstacle_location.z - vehicle_location.z)**2))
        print("Obstacle detected at distance: ", self.obstacle_distance)

    def Update(self):
        
        while self.run:
                try:
                    self.world.tick()
                    self.Ego_Movement()
                    self.Speedometer()
                    self.Speed_Limit()
                except:
                    pass
          
if __name__ == "__main__":
    simulator = Carla()
    simulator.Update()
    #simulator.Despawn_All_Vehicles()
    #simulator.LoadTown()