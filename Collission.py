#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import carla
import numpy as np
import time

def avoid_collision(vehicle, other_vehicles):
    """
    Function to avoid collision with other vehicles.

    :param vehicle: the ego vehicle
    :param other_vehicles: list of other vehicles in the environment
    """
    for other_vehicle in other_vehicles:
        if vehicle.id == other_vehicle.id:
            continue

        # Get the relative position and velocity of the other vehicle
        relative_position = np.array([other_vehicle.get_location().x - vehicle.get_location().x,
                                      other_vehicle.get_location().y - vehicle.get_location().y,
                                      other_vehicle.get_location().z - vehicle.get_location().z])
        relative_velocity = np.array([other_vehicle.get_velocity().x - vehicle.get_velocity().x,
                                      other_vehicle.get_velocity().y - vehicle.get_velocity().y,
                                      other_vehicle.get_velocity().z - vehicle.get_velocity().z])

        # Check if the other vehicle is in front of the ego vehicle
        if np.dot(relative_position, relative_velocity) > 0:
            # Check if the other vehicle is close to the ego vehicle
            if np.linalg.norm(relative_position) < 20.0:
                # Brake the ego vehicle to avoid collision
                vehicle.apply_control(carla.VehicleControl(throttle=0.0, brake=1.0))
                time.sleep(0.5)

# Connect to the CARLA simulator
client = carla.Client("localhost", 2000)
client.set_timeout(2.0)
world = client.get_world()

# Get the ego vehicle
vehicle = world.get_actor("vehicle0")

# Continuously check for collisions
while True:
    other_vehicles = world.get_actors().filter("vehicle.*")
    avoid_collision(vehicle, other_vehicles)

