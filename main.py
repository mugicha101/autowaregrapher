from ros2cli.node.strategy import NodeStrategy
from ros2node.api import get_publisher_info, get_subcriber_info
from ros2topic.api import get_topic_names_and_types

node_name = "/sensing/lidar/top/velodyne_ros_wrapper_node"
topic_name = "/sensing/lidar/top/pointcloud_raw_ex"
node = NodeStrategy(node_name)
get_subcriber_info(node=node, remote_node_name=node_name)
get_publisher_info(node=node, remote_node_name=node_name)
node.get_subscriptions_info_by_topic(topic_name)
node.get_publishers_info_by_topic(topic_name)