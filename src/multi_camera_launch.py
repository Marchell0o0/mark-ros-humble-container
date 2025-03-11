#!/usr/bin/env python3

import os
import yaml
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import TimerAction, DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
from launch.conditions import IfCondition

def generate_launch_description():
    # Define launch arguments
    camera_config_arg = DeclareLaunchArgument(
        'camera_config',
        default_value='src/cameras.yml',
        description='Path to the camera configuration YAML file'
    )
    
    # Get the camera config path from the launch argument
    camera_config_path = LaunchConfiguration('camera_config')
    
    # Define a function to load the config when the launch file is executed
    def get_camera_config(context):
        config_file = context.perform_substitution(camera_config_path)
        
        # Check if the file exists
        if not os.path.exists(config_file):
            # Try with package path
            try:
                pkg_dir = get_package_share_directory('mark_interactive_properties')
                alt_config_file = os.path.join(pkg_dir, 'cameras.yml')
                if os.path.exists(alt_config_file):
                    config_file = alt_config_file
            except:
                print(f"Warning: Could not find camera config at {config_file}")
                return []
        
        # Load camera configurations from YAML
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        # Extract the physical cameras (skip logical camera references)
        cameras = []
        for camera_id, camera_config in config['cameras'].items():
            # Skip logical camera aliases that use other cameras
            if 'use_camera' in camera_config:
                continue
                
            # Extract the necessary configuration for the launch
            cameras.append({
                "role_name": camera_id,  # top_camera or scene_camera
                "name": camera_config['name'],  # camera1 or camera2
                "serial_no": camera_config['serial_no'],
                "color_profile": camera_config.get('color_profile', '1280x720x15'),
                "depth_profile": camera_config.get('depth_profile', '1280x720x5')
            })
        
        return cameras
    
    # Use OpaqueFunction to defer loading the config until the launch context is available
    from launch.actions import OpaqueFunction
    
    # Create a function to set up the camera nodes
    def launch_setup(context):
        cameras = get_camera_config(context)
        
        # Create a node for each camera
        nodes = []
        
        for idx, camera in enumerate(cameras):
            # Try using device_type and serial_no first, with usb_port_id as fallback
            parameters = [
                {"serial_no": str(camera["serial_no"])},  # Try as integer
                # Other standard parameters
                {"camera_name": camera["name"]},
                {"rgb_camera.color_profile": camera["color_profile"]},
                {"depth_module.depth_profile": camera["depth_profile"]},
                {"log_level": "info"},
                {"enable_color": True},
                {"enable_depth": True},
            ]
            
            node = Node(
                package="realsense2_camera",
                executable="realsense2_camera_node",
                name=camera["name"],
                namespace=camera["name"],
                parameters=parameters,
                output="screen",
                emulate_tty=True,
                arguments=["--ros-args", "--log-level", "info"]
            )
            
            # Add a small delay between camera launches to avoid USB bandwidth issues
            if idx > 0:
                # Add 2-second delay before launching subsequent cameras
                node = TimerAction(
                    period=2.0,
                    actions=[node]
                )
                
            nodes.append(node)
        
        return nodes
    
    # Return the LaunchDescription
    return LaunchDescription([
        camera_config_arg,
        OpaqueFunction(function=launch_setup)
    ]) 