import glob
import os
import sys
import random
import networkx as nx

## Find Carla Module
try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

def path_finder(start_location, goal_location, map_):
    """
    Find the shortest path between start and goal locations using A* algorithm.

    :param start_location: starting location
    :param goal_location: goal location
    :param map_: CARLA map object
    :return: list of waypoints between start and goal locations
    """
    graph = nx.Graph()

    # Get all the roads in the map
    for waypoint in map_.generate_waypoints(2.0):
        graph.add_node((waypoint.transform.location.x, waypoint.transform.location.y))
        for next_waypoint in waypoint.next(2.0):
            distance = waypoint.transform.location.distance(next_waypoint.transform.location)
            graph.add_edge((waypoint.transform.location.x, waypoint.transform.location.y),
                            (next_waypoint.transform.location.x, next_waypoint.transform.location.y),
                            weight=distance)

    # Find the shortest path between start and goal locations
    try:
        path = nx.astar_path(graph, (start_location.x, start_location.y), (goal_location.x, goal_location.y), heuristic=None)
    except nx.NetworkXNoPath:
        return None

    waypoints = []
    for i in range(len(path) - 1):
        waypoint = map_.get_waypoint(carla.Location(*path[i]))
        next_waypoint = map_.get_waypoint(carla.Location(*path[i+1]))
        waypoints.extend(waypoint.next(2.0, max_length=waypoint.transform.location.distance(next_waypoint.transform.location)))

    return waypoints

# Connect to the CARLA simulator
client = carla.Client("localhost", 2000)
client.set_timeout(2.0)
world = client.get_world()

# Get the CARLA map
map_ = world.get_map()

# Specify the start and goal locations
start_location = carla.Location(x=53.53, y=-53.53, z=0.0)
goal_location = carla.Location(x=-53.53, y=53.53, z=0.0)

# Find the shortest path between start and goal locations
waypoints = path_finder(start_location, goal_location, map_)

# Display the waypoints
if waypoints:
    for waypoint in waypoints:
        print(waypoint.transform.location)
else:
    print("No path found between start and goal locations")

    