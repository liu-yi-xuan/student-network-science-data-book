# Network Community Detection and Visualization

This repository provides a set of functions to perform community detection on networks using algorithms like Girvan-Newman and Louvain. Additionally, it includes utilities to calculate modularity and visualize the detected communities with various layouts.

## Functions Overview

### 1. `calculate_modularity(G, partition)`
This function calculates the modularity of a given partition of a graph `G`. Modularity is a measure of the strength of division of a network into communities.

- **Parameters**:
  - `G` (networkx.Graph): The input graph.
  - `partition` (list of sets or dict): The partition of the graph where each set (or dict) represents a community.
  
- **Returns**:
  - `float`: The modularity score.

### 2. `get_modularity(G, partition)`
This function calculates the modularity of the current partition using an alternative method based on node degrees and community assignments.

- **Parameters**:
  - `G` (networkx.Graph): The graph for which modularity is to be calculated.
  - `partition` (dict): A dictionary where keys are nodes and values are community labels.
  
- **Returns**:
  - `float`: The modularity score.

### 3. `local_optimization_step(H, Q_max)`
This function performs a local optimization step on the graph to maximize modularity by moving nodes to neighboring communities.

- **Parameters**:
  - `H` (networkx.Graph): The graph with community assignments as node attributes.
  - `Q_max` (float): The current maximum modularity.
  
- **Returns**:
  - `float`: The updated maximum modularity after the optimization step.

### 4. `network_aggregation_step(H)`
This function performs the network aggregation step by collapsing communities into super-nodes and recalculating edge weights between communities.

- **Parameters**:
  - `H` (networkx.Graph): The graph where each node has a 'community' attribute.
  
- **Returns**:
  - `networkx.Graph`: A new graph where nodes represent communities from the previous step.

### 5. `reindex_communities(partition)`
This function reindexes the communities in the partition so that community labels are continuous.

- **Parameters**:
  - `partition` (dict): A dictionary where keys are nodes and values are community labels.
  
- **Returns**:
  - `dict`: A new partition where community labels are reindexed.

### 6. `louvain_method(G, init=None)`
This function runs the Louvain method for community detection on a graph.

- **Parameters**:
  - `G` (networkx.Graph): The input graph where nodes and edges define the structure.
  - `init` (dict): Optional initial partition.
  
- **Returns**:
  - `dict`: The final partition of the graph with node assignments to communities.

### 7. `vis_network_spring(G, best_partition, layout_type="spring_layout")`
This function visualizes a network with a specified layout, coloring nodes by community.

- **Parameters**:
  - `G` (networkx.Graph): The graph to visualize.
  - `best_partition` (dict): A partition of the graph nodes (community assignments).
  - `layout_type` (str): The layout algorithm to use. Options are "spring_layout", "shell_layout", and "kamada_kawai_layout".
  
- **Returns**:
  - `None`: Displays the network graph.

### 8. `vis_network_agg_spring(G, best_partition, layout1="shell_layout", iterations=1)`
This function visualizes a network using an aggregated layout approach. The first layout is either 'shell_layout' or 'kamada_kawai_layout', and the second layout is always 'spring_layout' for a specified number of iterations.

- **Parameters**:
  - `G` (networkx.Graph): The graph to visualize.
  - `best_partition` (dict): A partition of the graph nodes (community assignments).
  - `layout1` (str): The first layout algorithm to use, either 'shell_layout' or 'kamada_kawai_layout'.
  - `iterations` (int): The number of iterations for the 'spring_layout' adjustment.
  
- **Returns**:
  - `None`: Displays the network graph.

### 9. `vis_network_partition_process(G, pos=None, method="girvan_newman", w=5.0, h=4.0, nrows=6, ncols=6, iterations_limit=None)`
This function visualizes the partitioning process of a network using the Girvan-Newman algorithm.

- **Parameters**:
  - `G` (networkx.Graph): The input graph.
  - `pos` (dict or None): Positions for the nodes in the graph. If None, default spring_layout will be used.
  - `method` (str): Only "girvan_newman" is supported.
  - `w` (float): Width of each subplot.
  - `h` (float): Height of each subplot.
  - `nrows` (int): Number of rows in the grid of subplots.
  - `ncols` (int): Number of columns in the grid of subplots.
  - `iterations_limit` (int): Limit the number of iterations to display.
  
- **Returns**:
  - `None`: Displays the partitioning process.
