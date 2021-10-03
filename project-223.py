import glob
import os
import sys
import time
import random
try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

actor_list = []


def generate_radar_blueprint(blueprint_library):
    radar_blueprint = blueprint_library.filter('sensor.other.radar')[0]
    radar_blueprint.set_attribute('horizontal_fov', str(40))
    radar_blueprint.set_attribute('vertical_fov', str(30))
    radar_blueprint.set_attribute('points_per_second', str(15000))
    radar_blueprint.set_attribute('range', str(20))
    return radar_blueprint

def check_traffic_lights():
    if dropped_vehicle.is_at_traffic_light():
        traffic_light = dropped_vehicle.get_traffic_light()
        if traffic_light.get_state() == carla.TrafficLightState.Red:
            print(traffic_light.get_state())
            dropped_vehicle.apply_control(carla.VehicleControl(hand_brake=True))
    else:
        dropped_vehicle.apply_control(carla.VehicleControl(throttle=0.50))


try:
    client = carla.Client('127.0.0.1', 2000)
    client.set_timeout(10.0)
    world = client.get_world()

    get_blueprint_of_world = world.get_blueprint_library()
    car_model = get_blueprint_of_world.filter('model3')[0]
    # Follow the following numbers to apply car color
    # '17,37,103' = Blue 1
    # '75,87,173' = Blue 2
    # '180,44,44' = Red 1
    # '180,180,180' = Silver
    # '44,44,44' = Black
    # '137,0,0' = Red 2
    car_color='180,180,180'#get the color code and store it in car_color
    car_model.set_attribute('color',car_color)#apply color using set_attribute on car_model
    spawn_point = (world.get_map().get_spawn_points()[31])
    dropped_vehicle = world.spawn_actor(car_model, spawn_point)


    simulator_camera_location_rotation = carla.Transform(spawn_point.location, spawn_point.rotation)
    simulator_camera_location_rotation.location += spawn_point.get_forward_vector() * 30
    simulator_camera_location_rotation.rotation.yaw += 180
    simulator_camera_view = world.get_spectator()
    simulator_camera_view.set_transform(simulator_camera_location_rotation)
    actor_list.append(dropped_vehicle)

    radar_sensor = generate_radar_blueprint(get_blueprint_of_world)
    sensor_radar_spawn_point = carla.Transform(carla.Location(x=-0.5, z=1.8))
    sensor = world.spawn_actor(radar_sensor, sensor_radar_spawn_point, attach_to=dropped_vehicle)

    sensor.listen(lambda radar_data: _Radar_callback(radar_data))

    def _Radar_callback(radar_data):
        distance_name_data = {}
        for detection in radar_data:
            distance_name_data["distance"] = detection.depth
            if distance_name_data["distance"] > 3 and distance_name_data["distance"] < 6:#Write If condition to check distance 3 to 6 meters
            	print("Brake")
            	dropped_vehicle.apply_control(carla.VehicleControl(hand_brake=True))#write a code to apply brake 
            	waypoint =world.get_map().get_waypoint(dropped_vehicle.get_location(),project_to_road=True, lane_type=(carla.LaneType.Driving |carla.LaneType.Shoulder | carla.LaneType.Sidewalk))#get the waypoint for where your car running
            	print("Current lane type: " + str(waypoint.lane_type))#print current lane
            	break
            else:
                check_traffic_lights()

    actor_list.append(sensor)
    check_traffic_lights()
    time.sleep(1000)
finally:
    print('destroying actors')
    for actor in actor_list:
        actor.destroy()
    print('done.')
