import carla
import time

IP_ADDRESS = 'localhost'
PORT = 2000
TIMEOUT = 10
TOWN = 'Town05'


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
    
    def LoadTown(self):
        self.town = self.client.load_world(TOWN)
        print("Town Loaded")

    def on_collision(self, event, _):
        collision = event.other_actor
        print("Vehicle collided with", collision.type_id)
        self.ego_vehicle.destroy()

    def Collision_Sensors(self):
        self.colsensor_bp = self.blueprints.find('sensor.other.collision')
        self.colsensor_transform = carla.Transform(carla.Location(x=1.0, z=1.0))
    
    def Collision_Event(self):
        try:
            self.colsensor = self.world.spawn_actor(self.colsensor_bp, self.colsensor_transform, attach_to=self.ego_vehicle)
            self.colsensor.listen(lambda event: self.on_collision(event, self))
        except Exception as e:
            print("Exception occurred:", e)

    def Spawn_Vehicle(self):
        ego_vehicle_bp = self.blueprints.find('vehicle.tesla.model3')
        location = carla.Transform(carla.Location(x=30, y=6, z=1), carla.Rotation(yaw=0))
        self.ego_vehicle = self.world.try_spawn_actor(ego_vehicle_bp, location)
        self.Collision_Sensors()

    def Despawn_All_Vehicles(self):
        actor_list = self.world.get_actors()
        for actor in actor_list:
            if 'vehicle' in actor.type_id:
                actor.destroy()
                print("Vehicle Deleted")

    def Ego_Movement(self):
        self.ego_vehicle.apply_control(carla.VehicleControl(throttle=1, steer=0))

    def Update(self):
        run = True
        while run:
            self.Spawn_Vehicle()
            self.Collision_Event()
            self.Ego_Movement()
            

if __name__ == "__main__":
    simulator = Carla()
    simulator.Update()
    #simulator.Despawn_All_Vehicles()
    #simulator.LoadTown()
