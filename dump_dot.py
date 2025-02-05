import networkx as nx
from collections import defaultdict, deque
import matplotlib.pyplot as plt
import math

graph = nx.drawing.nx_pydot.read_dot("autoware_2024.12_0.39.0.dot")

# reformat names
shortened_names = True
def rename(node):
  return node.removeprefix("n___").replace("__", "/").split("/")[-1]
mapping = dict([ (node, rename(node)) for node in graph.nodes() ])
graph = nx.relabel_nodes(graph, mapping)

for name in graph.nodes():
  print(name)
for src, dst in graph.edges():
  print(f"{src} -> {dst}")

# construct subgraph of nodes that can reach target (use bfs for distance)
target = "planning/scenario_planning/lane_driving/motion_planning/obstacle_cruise_planner".split("/")[-1]
subgraph_nodes = set()
subgraph_nodes.add(target)
layers = [[target]]
while len(layers[-1]) > 0:
  layers.append([])
  for node in layers[-2]:
    for src, dst in graph.in_edges(node):
      if src in subgraph_nodes: continue
      subgraph_nodes.add(src)
      layers[-1].append(src)
layers.pop()
print(layers)

# assign positions to nodes based on distance from target
subgraph = nx.subgraph(graph, subgraph_nodes)

pos = {}
label_pos = {}
x_gap = 400
y_gap = 200
for dist, layer in enumerate(layers):
  offset = (len(layer) - 1) * -0.5
  for idx, node in enumerate(layer):
    x = x_gap * (idx + offset)
    y = y_gap * -(dist + (idx % 3) * 0.1)
    pos[node] = (x, y)
    label_pos[node] = (x, y - y_gap * 0.2)

# plot graph
plt.figure(figsize=(12, 8))
nx.draw(
    subgraph, 
    pos=pos,
    with_labels=False,
    node_size=y_gap * 0.5, 
    node_color="lightblue",
    arrowsize=5,
    width=0.2,
    edge_color="blue"
)
nx.draw_networkx_labels(
  subgraph,
  pos=label_pos,
  font_size=3,
)
plt.title(f"Ancestor Subgraph of {target}")
plt.savefig("graph.svg")