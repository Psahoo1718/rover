import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    package_name = 'rover_description'
    xacro_file_name = 'rover_description.urdf.xacro'

    
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(
                get_package_share_directory('gazebo_ros'),
                'launch',
                'gazebo.launch.py'
            )
        ])
    )

   
    static_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='tf_footprint_base',
        arguments=['0', '0', '0', '0', '0', '0', 'chassis', 'base_footprint']
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': ParameterValue(
                Command([
                    'xacro ',
                    PathJoinSubstitution([
                        FindPackageShare(package_name),
                        'urdf',
                        xacro_file_name
                    ])
                ]),
                value_type=str
            )
        }]
    )

    # Spawn robot (after 5 seconds)
    spawn_entity = TimerAction(
        period=5.0,
        actions=[
            Node(
                package='gazebo_ros',
                executable='spawn_entity.py',
                name='spawn_model',
                arguments=[
                    '-topic', 'robot_description',
                    '-entity', 'rover_description',
                    '-x', '0.0', '-y', '0.0', '-z', '-0.6', '-R', '-1.5708', '-P', '0', '-Y', '0'
                ],
                output='screen'
            )
        ]
    )

    
    calibrate = ExecuteProcess(
        cmd=['ros2', 'topic', 'pub', '--once', '/calibrated', 'std_msgs/msg/Bool', '"{data: true}"'],
        shell=True
    )

    return LaunchDescription([
        gazebo,
        static_tf,
        robot_state_publisher,
        spawn_entity,
        calibrate
    ])
