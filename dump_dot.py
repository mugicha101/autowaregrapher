import networkx as nx
from collections import defaultdict, deque
import matplotlib.pyplot as plt
import gravis as gv
import math
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

# construct subgraphs of nodes on chain from sources to target
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

def src2dst_subgraph(graph, src, dst):
  aug_graph = graph.copy()
  aug_graph.remove_edges_from([ e for e in aug_graph.out_edges(dst) ])
  aug_graph.remove_edges_from([ e for e in aug_graph.in_edges(src) ])
  dst_anc = nx.ancestors(aug_graph, dst)
  src_dsc = nx.descendants(aug_graph, src)
  return nx.subgraph(graph, dst_anc.intersection(src_dsc).union({src, dst}))

subgraphs = {}
subgraph_nodes = set()
subgraphs[f"all_sources -> {target}"] = None # so that its first in the list
subgraphs[f"full"] = graph
for source in sources:
  g = src2dst_subgraph(graph, source, target)
  subgraph_nodes.update(set(g.nodes()))
  subgraphs[f"{source} -> {target}"] = g
  src_node = g.nodes[source]
  dst_node = g.nodes[target]
subgraphs[f"all_sources -> {target}"] = nx.subgraph(graph, subgraph_nodes)

# helpers for node attributes
def node_color(graph, node):
  # high level diagram: https://autowarefoundation.github.io/autoware-documentation/main/design/autoware-architecture/perception/#high-level-architecture
  # sensing, localization, map (greens/blues) -> perception (yellow) -> planning (pink)
  # adapi/api/control (reds/oranges)
  # system (brown)
  component = node.split(":")[1].split("/")[0]
  component_color = {
    "sensing": "rgb(0,0,255)",
    "localization": "rgb(0,255,255)",
    "map": "rgb(0,255,0)",
    "perception": "rgb(255,255,0)",
    "planning": "rgb(255,0,255)",
    "system": "rgb(128,64,0)",
    "api": "rgb(255,128,0)",
    "adapi": "rgb(255,64,0)",
    "control": "rgb(255,0,0)"
  }
  default_color = "rgb(200,200,200)"

  return component_color[component] if component in component_color else default_color

def node_border_color(graph, node):
  default_color = "rgb(0,0,0)"
  source_color = "rgb(0,255,0)"
  sink_color = "rgb(255,0,0)"
  singleton_color = "rgb(128,128,128)"
  indeg = len(graph.in_edges(node))
  outdeg = len(graph.out_edges(node))
  return singleton_color if indeg + outdeg == 0 else sink_color if outdeg == 0 else source_color if indeg == 0 else default_color

def node_shape(node):
  return "circle" if node.startswith("node:") else "rectangle"

def shorthand(node):
  return node.split(":")[1].split("/")[-1]

def node_size(graph, node):
  return (1 + 0.25 * math.sqrt(len(graph.in_edges(node)) + len(graph.out_edges(node)))) * 15

def node_tooltip(graph, node, dist):
  return "\n".join([
    f"component: {node.split(":")[1].split("/")[0]}",
    f"indeg: {len(graph.in_edges(node))}",
    f"outdeg: {len(graph.out_edges(node))}",
    f"sink distance: {min(dist[node][sink] for sink in graph if (len(graph.out_edges(sink)) == 0) and node in dist and sink in dist[node])}",
    f"source distance: {min(dist[source][node] for source in graph if (len(graph.in_edges(source)) == 0) and source in dist and node in dist[source])}"
  ])


# convert to gravis graph
def to_gravis_graph(name, graph):
  dist = dict(nx.all_pairs_shortest_path_length(graph))
  gvg = { "graph": {
    "label": name,
    "directed": True,
    "metadata": {
      "arrow_size": 15,
      "background_color": "white",
      "edge_size": 2,
      "node_border_size": 3
    },
    "nodes": dict((node, {
      "metadata": {
        "shape": node_shape(node),
        "color": node_color(graph, node),
        "size": node_size(graph, node),
        "border_color": node_border_color(graph, node),
        "hover": node_tooltip(graph, node, dist)
      }
    }) for node in graph),
    "edges": [
      { "source": src, "target": dst }
    for src, dst in graph.edges() ]
  }}

  for node, data in gvg["graph"]["nodes"].items():
    meta = data["metadata"]
    indeg = len(graph.in_edges(node))
    outdeg = len(graph.out_edges(node))
    if indeg + outdeg == 0:
      pass
    elif indeg == 0:
      meta["x"] = -6000
    elif outdeg == 0:
      meta["x"] = 6000
  return gvg

# generate gravis html
render_graphs = [ to_gravis_graph(name, subgraph) for name, subgraph in subgraphs.items() ]
fig = gv.d3(
  render_graphs,
  use_node_size_normalization=False,
  use_edge_size_normalization=False,
  links_force_strength=1.0,
  links_force_distance=300,
  many_body_force_strength=-850,
  use_y_positioning_force=True,
  y_positioning_force_strength=0.01,
  edge_size_data_source='weight',
  edge_curvature=0.05,
  zoom_factor=0.2,
  node_hover_neighborhood=True,
  node_drag_fix=True,
  use_centering_force=False,
  use_collision_force=True
)
if os.path.exists("out.html"): os.remove("out.html")
with open("out.html", "w", encoding="utf-8") as file:
  html = fig.to_html()
  file.write(html)
