import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime
import community  


transactions = [
......
    # Add more transactions as needed
]


G = nx.Graph()
for sender, receiver, weight in transactions:
    if not G.has_node(sender):
        G.add_node(sender)
    if not G.has_node(receiver):
        G.add_node(receiver)

    G.add_edge(sender, receiver, weight=weight)


partition = community.best_partition(G)

pos = nx.spring_layout(G)
plt.figure(figsize=(10, 6))
cmap = plt.get_cmap('viridis', max(partition.values()) + 1)
nx.draw_networkx_nodes(G, pos, node_color=[cmap(partition[node]) for node in G.nodes()])
nx.draw_networkx_edges(G, pos, alpha=0.5)
plt.title('Community Detection using Louvain Algorithm')
plt.show()


