from ros2cli.node.strategy import NodeStrategy
from ros2node.api import get_publisher_info, get_subcriber_info

node_name = "/sensing/lidar/top/velodyne_ros_wrapper_node"
node = NodeStrategy(node_name)
get_subcriber_info(node=node, remote_node_name=node_name)
get_publisher_info(node=node, remote_node_name=node_name)