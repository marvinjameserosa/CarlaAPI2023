import carla
import numpy as np
import cv2
import os

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

camera_bp = blueprints.find('sensor.camera.rgb')
camera_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
camera = world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle)

def process_image(image, image_count):
    image.convert(carla.ColorConverter.Raw)
    raw_image = np.array(image.raw_data)
    raw_image = raw_image.reshape((image.height, image.width, 4))
    raw_image = raw_image[:, :, :3]
    cv2.imshow("Camera View", raw_image)
    cv2.waitKey(1)

    folder_path = r'C:\Users\mjae0\OneDrive\Desktop\CARLA experiments\CarlaAPI2023\BASIC CONCEPTS\images'
    os.makedirs(folder_path, exist_ok=True)
    image_filename = os.path.join(folder_path, f'image_{image_count}.png')
    cv2.imwrite(image_filename, raw_image)

image_count = 0
camera.listen(lambda image: process_image(image, image_count))


while True:
    world.tick()
    image_count += 1
