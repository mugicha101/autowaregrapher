import networkx as nx
from collections import defaultdict, deque
import matplotlib.pyplot as plt
import gravis as gv
import os

graph = nx.drawing.nx_pydot.read_dot("autoware_2024.12_0.39.0.dot")

# add nodes for topics
new_graph = nx.MultiDiGraph()
for node in graph.nodes():
  new_graph.add_node(node, **graph.nodes[node])
for src, dst in graph.edges():
  attr = graph[src][dst][0]
  topic = attr["URL"]
  new_graph.add_node(topic, **attr)
  new_graph.add_edge(src, topic)
  new_graph.add_edge(topic, dst)
graph = new_graph

# refactor names
def rename(node):
  return ("node:" if node.startswith("n___") else "topic:") + node.removeprefix("n___").removeprefix("topic_3A__").replace("__", "/")
mapping = dict([ (node, rename(node)) for node in graph.nodes() ])
graph = nx.relabel_nodes(graph, mapping)

for name in graph.nodes():
  print(name)
for src, dst in graph.edges():
  print(f"{src} -> {dst}")

# construct subgraph of nodes that can reach target (use bfs for distance)
# TODO: filter further using source and dest nodes
target = "node:planning/scenario_planning/lane_driving/motion_planning/obstacle_cruise_planner"
sources = [
  "topic:sensing/lidar/top/velodyne_packets",
  "topic:sensing/lidar/left/velodyne_packets",
  "topic:sensing/lidar/right/velodyne_packets",
  "topic:sensing/camera/camera6/image_raw",
  "topic:sensing/camera/camera7/image_raw",
  "topic:sensing/imu/tamagawa/imu_raw",
  "topic:sensing/gnss/ublox/nav_sat_fix",
]

def descendant_subgraph(graph, node):
  return nx.subgraph(graph, nx.descendants(graph, node).union({node}))

def ancestor_subgraph(graph, node):
  return nx.subgraph(graph, nx.ancestors(graph, node).union({node}))

def src2dst_subgraph(graph, src, dst):
  return nx.intersection(descendant_subgraph(graph, src), ancestor_subgraph(graph, dst))

subgraphs = {}
for source in sources:
  g = src2dst_subgraph(graph, source, target)
  subgraphs[f"{source} -> {target}"] = g
  src_node = g.nodes[source]
  dst_node = g.nodes[target]
  src_node["x"], src_node["y"] = -10000, 0
  dst_node["x"], dst_node["y"] = 10000, 0
subgraphs[f"all_sources -> {target}"] = nx.compose_all(graph for source, graph in subgraphs.items())
subgraphs[f"full"] = graph

def node_color(graph, node):
  root_color = "rgb(0,255,0)"
  dst_color = "rgb(255,0,0)"
  node_color = "rgb(0,255,255)"
  topic_color = "rgb(0,0,255)"
  
  return dst_color if node == target else root_color if len(graph.in_edges(node)) == 0 else node_color if node.startswith("node:") else topic_color

def node_shape(node):
  return "circle" if node.startswith("node:") else "rectangle"

def shorthand(node):
  return node.split(":")[1].split("/")[-1]

# convert to gravis graph
def to_gravis_graph(name, graph):
  node_text = [ shorthand(node) for node in graph ]
  node_hovertext = [ node for node in graph ]
  gvg = { "graph": {
    "label": name,
    "directed": True,
    "metadata": {
      "arrow_size": 15,
      "background_color": "white",
      "edge_size": 2,
      "node_size": 20
    },
    "nodes": dict((node, {
      "metadata": {
        "shape": node_shape(node),
        "color": node_color(graph, node)
      }
    }) for node in graph),
    "edges": [
      { "source": src, "target": dst }
    for src, dst in graph.edges() ]
  }}

  for node, data in gvg["graph"]["nodes"].items():
    meta = data["metadata"]
    if node == target:
      meta["x"] = 10000
    if len(graph.in_edges(node)) == 0:
      meta["x"] = -10000
  return gvg

# generate gravis html
render_graphs = [ to_gravis_graph(name, subgraph) for name, subgraph in subgraphs.items() ]
fig = gv.d3(
  render_graphs,
  use_node_size_normalization=True,
  node_size_factor=5,
  use_edge_size_normalization=True,
  links_force_strength=1.0,
  links_force_distance=300,
  many_body_force_strength=-850,
  use_y_positioning_force=True,
  y_positioning_force_strength=0.05,
  edge_size_data_source='weight',
  edge_curvature=0.2,
  zoom_factor=0.2
)
if os.path.exists("out.html"): os.remove("out.html")
with open("out.html", "w", encoding="utf-8") as file:
  html = fig.to_html()
  file.write(html)
