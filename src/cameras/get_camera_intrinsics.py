#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
import yaml
import numpy as np
import os
import argparse
from sensor_msgs.msg import CameraInfo

class CameraIntrinsicsNode(Node):
    def __init__(self, yaml_file, logical_camera_name):
        super().__init__('camera_intrinsics_node')
        self.yaml_file = yaml_file
        self.logical_camera_name = logical_camera_name
        self.info_received = False
        
        # First load the YAML file to get the physical camera name
        try:
            with open(yaml_file, 'r') as file:
                config = yaml.safe_load(file)
                
            if 'cameras' in config and logical_camera_name in config['cameras']:
                physical_camera = config['cameras'][logical_camera_name]['name']
                self.get_logger().info(f'Mapped logical camera {logical_camera_name} to physical camera {physical_camera}')
            else:
                self.get_logger().error(f'Camera {logical_camera_name} not found in YAML configuration')
                rclpy.shutdown()
                return
        except Exception as e:
            self.get_logger().error(f'Error loading YAML file: {e}')
            rclpy.shutdown()
            return
        
        # Subscribe to camera info topics
        topic = f'/{physical_camera}/{physical_camera}/color/camera_info'
        self.subscription = self.create_subscription(
            CameraInfo,
            topic,
            self.camera_info_callback,
            10)
        
        self.get_logger().info(f'Listening for camera info on {topic}')
        
    def camera_info_callback(self, msg):
        if self.info_received:
            return
            
        # Extract camera matrix (K) and distortion coefficients (D)
        k = np.array(msg.k).reshape(3, 3).tolist()
        d = msg.d.tolist()
        
        self.get_logger().info(f'Received camera info for {self.logical_camera_name}')
        self.get_logger().info(f'Camera Matrix:\n{k}')
        self.get_logger().info(f'Distortion Coefficients: {d}')
        
        # Update YAML file
        try:
            # Load current YAML
            if os.path.exists(self.yaml_file):
                with open(self.yaml_file, 'r') as file:
                    config = yaml.safe_load(file)
            else:
                self.get_logger().error(f'YAML file not found: {self.yaml_file}')
                return
                
            # Update camera calibration
            if 'cameras' in config and self.logical_camera_name in config['cameras']:
                config['cameras'][self.logical_camera_name]['calibration']['camera_matrix'] = k
                config['cameras'][self.logical_camera_name]['calibration']['dist_coeffs'] = d
                
                # Write updated YAML
                with open(self.yaml_file, 'w') as file:
                    yaml.dump(config, file, default_flow_style=False)
                
                self.get_logger().info(f'Updated {self.yaml_file} with new calibration for {self.logical_camera_name}')
            else:
                self.get_logger().error(f'Camera {self.logical_camera_name} not found in YAML configuration')
                
        except Exception as e:
            self.get_logger().error(f'Error updating YAML file: {e}')
            
        self.info_received = True
        
        # We only need to get the info once, so we can destroy the node after updating
        rclpy.shutdown()

def main():
    parser = argparse.ArgumentParser(description='Get camera intrinsics and update YAML file')
    parser.add_argument('--yaml', type=str, default='src/cameras/cameras.yml',
                        help='Path to cameras.yml file')
    parser.add_argument('--camera', type=str, required=True,
                        help='Logical camera name in the YAML file (e.g., top_camera, scene_camera)')
    args = parser.parse_args()
    
    rclpy.init()
    
    node = CameraIntrinsicsNode(args.yaml, args.camera)
    
    rclpy.spin(node)
    
    # Clean up
    node.destroy_node()
    if not rclpy.ok():
        rclpy.shutdown()

if __name__ == '__main__':
    main() 