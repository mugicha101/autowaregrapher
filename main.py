from ros2cli.node.strategy import NodeStrategy
from ros2node.api import get_publisher_info, get_subscriber_info
from ros2node.api import get_node_names
from ros2topic.api import get_topic_names
from collections import defaultdict

# to differentiate nodes from topics, use "node:" and "topic:" prefixes (nodes/topics generalized to comps)

# helpers to get info from node graph

link_node = NodeStrategy("/clock")

node_names = [ f"node:{name.full_name}" for name in get_node_names(node=link_node, include_hidden_nodes=True) ]
topic_names = [ f"topic:{name}" for name in get_topic_names(node=link_node, include_hidden_topics=True) ]
comp_names = node_names + topic_names

print(node_names)
print(topic_names)

def get_subs(comp_name):
  type, name = comp_name.split(":")
  if type == "node": return [ f"topic:{info.name}" for info in get_subscriber_info(node=link_node, remote_node_name=name) ]
  if type == "topic": return [ f"node:{info.full_name}" for info in link_node.get_publishers_info_by_topic(name) ]
  return None

def get_pubs(comp_name):
  type, name = comp_name.split(":")
  if type == "node": return [ f"topic:{info.name}" for info in get_publisher_info(node=link_node, remote_node_name=name) ]
  if type == "topic": return [ f"node:{info.full_name}" for info in link_node.get_publishers_info_by_topic(name) ]
  return None

# construct graph

pubs = defaultdict(list) # publishers of a comp
subs = defaultdict(list) # subscribers of a comp

for name in comp_names:
  subs[name] = get_subs(name)
  pubs[name] = get_pubs(name)

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
