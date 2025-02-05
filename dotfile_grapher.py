import networkx as nx
import matplotlib.pyplot as plt
from pydot import graph_from_dot_file

# Step 1: Read and convert the .dot file to a NetworkX graph
dot_file_path = 'autoware_2024.12_0.39.0.dot'
graphs = graph_from_dot_file(dot_file_path)
graph = nx.DiGraph(nx.nx_pydot.from_pydot(graphs[0]))

# Step 2: Define the sink node (target node)
target_node = "n___system__mrm_comfortable_stop_operator"

# Step 3: Find all nodes that can reach the target node (all ancestors)
reachable_nodes = set(nx.ancestors(graph, target_node))
reachable_nodes.add(target_node)  # Include the target itself
subgraph = graph.subgraph(reachable_nodes)

# Optional: Use a hierarchical layout for a clearer view of the flow
try:
    pos = nx.nx_agraph.graphviz_layout(subgraph, prog="dot")
except ImportError:
    # Fallback to spring layout if pygraphviz is not installed
    pos = nx.spring_layout(subgraph, seed=42)

# Step 4: Visualize the larger subgraph
plt.figure(figsize=(12, 8))
nx.draw(
    subgraph, 
    pos, 
    with_labels=True, 
    node_size=400, 
    node_color="lightblue", 
    font_size=8, 
    arrowsize=8
)
plt.title("All Nodes Leading to Comfortable Stop Operator")
plt.show()
