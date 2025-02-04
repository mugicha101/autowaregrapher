from ros2cli.node.strategy import NodeStrategy
from ros2node.api import get_publisher_info, get_subscriber_info
from ros2node.api import get_node_names
from ros2topic.api import get_topic_names
from collections import defaultdict

# to differentiate nodes from topics, use "node:" and "topic:" prefixes

# helpers to get info from node graph

link_node = NodeStrategy("/clock")

node_names = get_node_names(node=link_node, include_hidden_nodes=True)
topic_names = get_topic_names(node=link_node, include_hidden_topics=True)

print(node_names)
print(topic_names)
  
def get_node_subs(node_name):
  return [ "topic:" + info.name for info in get_subscriber_info(node=link_node, remote_node_name=node_name) ]

def get_node_pubs(node_name):
  return [ "topic:" + info.name for info in get_publisher_info(node=link_node, remote_node_name=node_name) ]

def get_topic_pubs(topic_name):
  return [ "node:" + info.name for info in link_node.get_publishers_info_by_topic(topic_name) ]

def get_topic_subs(topic_name):
  return [ "node:" + info.name for info in link_node.get_subscriptions_info_by_topic(topic_name) ]

# construct graph

pubs = defaultdict(list) # publishers of a topic/node
subs = defaultdict(list) # subscribers of a topic/node

for name in topic_names:
  subs[name] = get_topic_subs(name)
  pubs[name] = get_topic_pubs(name)

for name in node_names:
  subs[name] = get_node_subs(name)
  pubs[name] = get_node_pubs(name)

# find chains

dst = "node:object_stop_planner"
chains = []
curr_chain = [ dst ]
def dfs():
  # case root node:
  if len(pubs[curr_chain[-1]]) == 0:
    chains.append([ v for v in curr_chain ])
    chains[-1].reverse()
    return
  
  # case non-root node:
  for pub in pubs[curr_chain[-1]]:
    curr_chain.append(pub)
    dfs()
    curr_chain.pop()

print(chains)
