import carla
import cv2
import numpy as np

IP_ADDRESS = 'localhost'
PORT = 2000
TIMEOUT = 10
TOWN = 'Town05'
EGO_VEHICLE = 'vehicle.tesla.model3'
image_count = 0
''DETECTION_RADIUS = 50.0 # meters
DETECTION_ANGLE = 60.0 # degrees
DETECTION_Z_OFFSET = 0.5 # meters
DETECTION_PROXIMITY_THRESHOLD = 1.0 # meters''


class Carla():
    def __init__(self, image_count):
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
        self.Obstacle_Detector()
        self.Take_Pictures(image_count)

        # Game Loop
        self.run = True

        # Input
        self.raw_image = None
        self.collide = False
        self.speed = None

        # Output
        self.throttle = 1
        self.steer = 0
        self.breaking = 0
        self.obstacle_distance = 0
        self.obstacle_location = [0, 0, 0]

    def LoadTown(self):
        self.town = self.client.load_world(TOWN)
        print("Town Loaded")

    def Reset(self):
        pass

    def Despawn_All_Vehicles(self):
        actor_list = self.world.get_actors()
        for actor in actor_list:
            if 'vehicle' in actor.type_id:
                actor.destroy()
                print("Vehicle Deleted")

    def Ego_Movement(self):
        self.ego_vehicle.apply_control(carla.VehicleControl(throttle=self.throttle, steer=self.steer, brake=self.breaking))

    def Speed_Limit(self):
        if self.speed > 25:
            self.ego_vehicle.apply_control(carla.VehicleControl(brake=1))

    def Speedometer(self):
        self.velocity = self.ego_vehicle.get_velocity()
        self.speed = 3.6 * (self.velocity.x**2 + self.velocity.y**2 + self.velocity.z**2)**0.5
        print(self.speed, "km/h")

    def RGB_Cam_Sensors(self):
        self.camera_bp = self.blueprints.find('sensor.camera.rgb')
        self.camera_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
        self.camera = self.world.spawn_actor(self.camera_bp, self.camera_transform, attach_to=self.ego_vehicle)

    def Process_Image(self, image, image_count):
        image.convert(carla.ColorConverter.Raw)
        self.raw_image = np.array(image.raw_data)
        self.raw_image = self.raw_image.reshape((image.height, image.width, 4))
        self.raw_image = self.raw_image[:, :, :3]
        cv2.imshow("Camera View", self.raw_image)
        cv2.waitKey(1)

    def Take_Pictures(self, image_count):
        self.camera.listen(lambda image: self.Process_Image(image, image_count))

    def on_collision(self, event, _):
        collision = event.other_actor
        print("Vehicle collided with", collision.type_id)
        self.ego_vehicle.destroy()
        self.collide = True
        self.run = False

    def Collision_Sensors(self):
        self.colsensor_bp = self.blueprints.find('sensor.other.collision')
        self.colsensor_transform = carla.Transform(carla.Location(x=1.0, z=1.0))
        self.colsensor = None
        try:
            self.colsensor = self.world.spawn_actor(self.colsensor_bp, self.colsensor_transform, attach_to=self.ego_vehicle)
            self.colsensor.listen(lambda event: self.on_collision(event, self))
        except Exception as e:
            print("Exception occurred:", e)

	def Obstacle_Detector(self):
        # Create Lidar Sensor
        lidar_bp = self.blueprints.find('sensor.lidar.ray_cast')
        lidar_location = carla.Transform(carla.Location(x=0.8, z=1.7))
        self.lidar_sensor = self.world.spawn_actor(lidar_bp, lidar_location, attach_to=self.ego_vehicle)
    
        # Register Callback Function
        self.lidar_sensor.listen(lambda data: self.Process_Lidar_Data(data))
    
    def Process_Lidar_Data(self, lidar_data):
        # Process Lidar Data
        for detection in lidar_data:
            x = detection.point.x
            y = detection.point.y
            z = detection.point.z
            intensity = detection.intensity
            azimuth = detection.azimuth
            altitude = detection.altitude

            print(f"x: {x}, y: {y}, z: {z}, intensity: {intensity}, azimuth: {azimuth}, altitude: {altitude}")

    def Update(self, image_count):
        
        while self.run:
                try:
                    self.world.tick()
                    image_count += 1
                    self.Ego_Movement()
                    self.Speedometer()
                    self.Speed_Limit()
                except:
                    pass

           
            
if __name__ == "__main__":
    simulator = Carla(image_count)
    #simulator.Update(image_count)
    #simulator.Despawn_All_Vehicles()
    simulator.LoadTown()
