import networkx as nx
import matplotlib.pyplot as plt
from pydot import graph_from_dot_file

# Step 1: Read and convert the .dot file to a NetworkX graph
dot_file_path = 'autoware_2024.12_0.39.0.dot'
graphs = graph_from_dot_file(dot_file_path)
graph = nx.DiGraph(nx.nx_pydot.from_pydot(graphs[0]))

# Step 2: Define the sink node (target node)
target_node = "n___system__mrm_comfortable_stop_operator"

# Step 3: Find all nodes that can reach the target node using reverse traversal
reachable_nodes = nx.single_target_shortest_path(graph.reverse(), target_node).keys()
subgraph = graph.subgraph(reachable_nodes)

# Step 4: Visualize the subgraph
plt.figure(figsize=(12, 8))
pos = nx.spring_layout(subgraph, seed=42)  
nx.draw(
    subgraph, 
    pos, 
    with_labels=True, 
    node_size=400, 
    node_color="lightblue", 
    font_size=8, 
    arrowsize=8
)
plt.title("Nodes Leading to Comfortable Stop Operator")
plt.show()
