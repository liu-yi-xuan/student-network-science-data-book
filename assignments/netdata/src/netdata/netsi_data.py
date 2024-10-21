
import networkx as nx
from collections import defaultdict
from random import shuffle
import matplotlib.pyplot as plt
import numpy as np
import itertools as it

def calculate_modularity(G, partition):
    """
    Calculates the modularity score for a given partition of the graph, whether the graph is weighted or unweighted.
    
    Modularity is a measure of the strength of division of a network into communities. It compares the actual 
    density of edges within communities to the expected density if edges were distributed randomly. For weighted 
    graphs, the weight of the edges is taken into account.

    The modularity Q is calculated as:
    
    Q = (1 / 2m) * sum((A_ij - (k_i * k_j) / (2m)) * delta(c_i, c_j))

    where:
    - A_ij is the weight of the edge between nodes i and j (1 if unweighted).
    - k_i is the degree of node i (or the weighted degree for weighted graphs).
    - m is the total number of edges in the graph, or the total weight of the edges if the graph is weighted.
    - delta(c_i, c_j) is 1 if nodes i and j belong to the same community, and 0 otherwise.

    Parameters:
    -----------
    G : networkx.Graph
        The input graph, which can be undirected and either weighted or unweighted. The graph's nodes represent the 
        entities, and its edges represent connections between them.
    
    partition : list of sets
        A list of sets where each set represents a community. Each set contains the nodes belonging to that community. 
        For example, [{0, 1, 2}, {3, 4}] represents two communities, one with nodes 0, 1, and 2, and another with nodes 
        3 and 4.
    
    Returns:
    --------
    float
        The modularity score for the given partition of the graph. A higher score indicates stronger community structure, 
        and a lower (or negative) score suggests weak or no community structure.

    Notes:
    ------
    - If the graph has weights, they will be used in the modularity calculation. If no weights are present, the function 
      assumes each edge has a weight of 1 (i.e., unweighted).
    
    - The function assumes that all nodes in the graph are assigned to exactly one community. If any node is missing 
      from the community list, it is treated as not belonging to any community, and the results may not be accurate.
    
    - If the graph has no edges, the modularity is undefined, and this function will return 0 because the total number 
      of edges (2m) would be zero.
    
    Example:
    --------
    >>> import networkx as nx
    >>> G = nx.karate_club_graph()
    >>> communities = [{0, 1, 2, 3, 4}, {5, 6, 7, 8, 9, 10}]
    >>> modularity_score = calculate_modularity(G, communities)
    >>> print("Modularity:", modularity_score)
    
    References:
    -----------
    Newman, M. E. J., & Girvan, M. (2004). Finding and evaluating community structure 
    in networks. Physical Review E, 69(2), 026113.
    """
  
    def remap_partition(partition):
        """
        Converts and remaps a partition to a list-of-lists structure suitable for modularity calculations.

        This function remaps the input partition (whether it's in dictionary form or a flat list of community labels) 
        to a list-of-lists format, where each list represents a community and contains the nodes in that community. 
        The function also ensures that community labels are contiguous integers starting from 0, which is typically 
        required for modularity-based algorithms.
        """

        # if partition is a dictionary where the keys are nodes and values communities
        if type(partition)==dict:
            unique_comms = np.unique(list(partition.values()))
            comm_mapping = {i:ix for ix,i in enumerate(unique_comms)}
            for i,j in partition.items():
                partition[i] = comm_mapping[j]

            unique_comms = np.unique(list(partition.values()))
            communities = [[] for i in unique_comms]
            for i,j in partition.items():
                communities[j].append(i)
                
            return communities

        # if partition is a list of community assignments
        elif type(partition)==list and\
                not any(isinstance(el, list) for el in partition):
            unique_comms = np.unique(partition)
            comm_mapping = {i:ix for ix,i in enumerate(unique_comms)}
            for i,j in enumerate(partition):
                partition[i] = comm_mapping[j]

            unique_comms = np.unique(partition)
            communities = [[] for i in np.unique(partition)]
            for i,j in enumerate(partition):
                communities[j].append(i)

            return communities

        # otherwise assume input is a properly-formatted list of lists
        else:
            communities = partition.copy()
            return communities


    # We now should have a list-of-lists structure for communities
    communities = remap_partition(partition)
    
    # Total weight of edges in the graph (or number of edges if unweighted)
    if nx.is_weighted(G):
        m = G.size(weight='weight')
        degree = dict(G.degree(weight='weight'))  # Weighted degree for each node
    else:
        m = G.number_of_edges()  # Number of edges in the graph
        degree = dict(G.degree())  # Degree for each node (unweighted)

    # Modularity score
    modularity_score = 0.0
    
    # Loop over all pairs of nodes i, j within the same community
    for community in communities:
        for i in community:
            for j in community:
                # Get the weight of the edge between i and j, or assume weight 1 if unweighted
                if G.has_edge(i, j):
                    A_ij = G[i][j].get('weight', 1)  # Use weight if available, otherwise assume 1
                else:
                    A_ij = 0  # No edge between i and j

                # Expected number of edges (or weighted edges) between i and j in a random graph
                expected_edges = (degree[i] * degree[j]) / (2 * m)

                # Contribution to modularity
                modularity_score += (A_ij - expected_edges)

    # Normalize by the total number of edges (or total edge weight) 2m
    modularity_score /= (2 * m)


    return modularity_score

def get_modularity(G, partition):
    """
    Calculate the modularity of the current partition of the graph G.
    
    Parameters:
    G (networkx.Graph): The graph for which modularity is to be calculated.
    partition (dict): A dictionary where keys are nodes and values are community labels.

    Returns:
    float: The modularity score for the given partition.
    """
    E_c = defaultdict(float)
    k_c = defaultdict(float)
    
    M = 0.0
    for source_node, target_node, w in G.edges(data = True):
        M += w['weight'] 
        if partition[source_node] ==  partition[target_node]:
            E_c[partition[source_node]] += w['weight']
    
    degrees = G.degree(weight='weight') 
    for node in G.nodes():
        k_c[partition[node]] += degrees[node]
        
    Q = sum( [ (E_c[c]/M) - (k_c[c]/(2.0*M))**2   for c in k_c.keys()     ]   )
    return Q


def local_optimization_step(H, Q_max, verbose=False):
    """
    Perform a local optimization step on the graph to maximize modularity by 
    moving nodes to neighboring communities.

    Parameters:
    H (networkx.Graph): The graph with community assignments as node attributes.
    Q_max (float): The current maximum modularity.
    verbose (bool): If True, print the current iteration number.

    Returns:
    float: The updated maximum modularity after the optimization step.
    """
    nodes = list(H.nodes())
    shuffle(nodes)

    something_changed = True
    iteration = 0

    while something_changed:
        iteration += 1
        if verbose:
            print(f'Iteration: {iteration}')
        
        something_changed = False  # Reset flag for changes made this iteration
        
        for node_i in nodes:
            current_partition = nx.get_node_attributes(H, 'community')
            current_community = current_partition[node_i]
            best_community = current_community
            best_diffQ = 0
            
            # Calculate the modularity change for moving node to each neighbor's community
            for neighbor in H.neighbors(node_i):
                neighbor_community = H.nodes[neighbor]['community']
                if neighbor_community != current_community:  # Only move if different
                    current_partition[node_i] = neighbor_community  # Temporarily move
                    Q_current = get_modularity(H, current_partition)
                    diffQ = Q_current - Q_max

                    if diffQ > best_diffQ:
                        best_diffQ = diffQ
                        best_community = neighbor_community

            # Apply the best community change if it improves modularity
            if best_community != current_community:
                H.nodes[node_i]['community'] = best_community
                Q_max += best_diffQ
                something_changed = True
        
        shuffle(nodes)  # Shuffle nodes for the next iteration

    return Q_max


def network_aggregation_step(H):
    """
    Perform the network aggregation step by collapsing communities into super-nodes 
    and recalculating edge weights between communities.

    Parameters:
    H (networkx.Graph): The graph where each node has a 'community' attribute.

    Returns:
    networkx.Graph: A new graph where nodes represent communities from the previous step.
    """
    edges = defaultdict(float)  # Dictionary to store new edges between communities

    # Aggregate edges between communities
    for source_node, target_node, w in H.edges(data=True):
        c1 = H.nodes[source_node]['community']
        c2 = H.nodes[target_node]['community']

        # Sort communities to ensure consistent ordering
        edge = tuple(sorted((c1, c2)))

        # Sum the edge weights between communities
        edges[edge] += w['weight']

    # Create a new aggregated graph where nodes are communities
    H_new = nx.Graph()
    H_new.add_edges_from(edges.keys())
    nx.set_edge_attributes(H_new, values=edges, name='weight')

    # Set the community attribute of each node to itself (each node is its own community initially)
    for node in H_new.nodes():
        H_new.nodes[node]['community'] = node
    
    return H_new


def reindex_communities(partition):
    """
    Reindex the communities in the partition so that community labels are continuous.

    Parameters:
    partition (dict): A dictionary where keys are nodes and values are community labels.

    Returns:
    dict: A new partition where community labels are reindexed to start from 0.
    """
    # Create a mapping from old community labels to new indices
    new_index = {community: c for c, community in enumerate(set(partition.values()))}
    
    # Reindex the partition using the new indices
    partition = {node: new_index[community] for node, community in partition.items()}
    
    return partition


def louvain_method(G, init=None):
    """
    Run the Louvain method for community detection on a graph.

    Parameters:
    G (networkx.Graph): The input graph where nodes and edges define the structure.
    init (dict): Optional initial partition. If None, each node is its own community.

    Returns:
    dict: The final partition of the graph with node assignments to communities.
    """
    # Make a copy of the graph to modify
    H = G.copy()

    # Initialize partition where each node is its own community, or use the provided initial partition
    if init:
        best_partition = init.copy()
    else:
        best_partition = {node: c for c, node in enumerate(H.nodes())}
    nx.set_node_attributes(H, values=best_partition, name='community')

    # Map each community to its original set of nodes
    aggregate_to_original = {node: [node] for node in H.nodes()}

    # Initialize edge weights if not present
    weights = {(node_i, node_j): 1.0 for node_i, node_j in H.edges()}
    nx.set_edge_attributes(H, values=weights, name='weight')

    # Compute initial modularity
    Q_max = calculate_modularity(H, best_partition)

    N = len(H)  # Number of nodes (communities)
    N_prev = -1  # Previous number of communities

    # Main loop: optimize modularity and aggregate communities until no change
    while N != N_prev:
        # 1) Perform local modularity optimization
        Q_max = local_optimization_step(H, Q_max)

        # Get the new community assignments after optimization
        best_partition_aggregate = nx.get_node_attributes(H, 'community')

        # Update the mapping from original nodes to new communities
        aggregate_to_original_old = aggregate_to_original.copy()
        aggregate_to_original = defaultdict(list)
        for old_community, new_community in best_partition_aggregate.items():
            for node in aggregate_to_original_old[old_community]:
                aggregate_to_original[new_community].append(node)
                best_partition[node] = new_community

        # 2) Perform network aggregation to create a new graph
        H = network_aggregation_step(H)

        # Update the number of nodes (communities)
        N_prev = N
        N = H.number_of_nodes()

    # Reindex the final community labels for clarity
    best_partition = reindex_communities(best_partition)

    return best_partition

def vis_network_spring(G, best_partition, layout_type="spring_layout"):
    """
    Visualize a network with a simple layout, coloring by community.

    Parameters:
    G (networkx.Graph): The graph to visualize
    best_partition (dict): A partition of the graph nodes (community assignments)
    layout_type (str): The layout algorithm to use. Options are "spring_layout", "forceatlas2_layout", "shell_layout", "kamada_kawai_layout"

    Returns:
    None: Displays the network graph
    """
    # Choose the layout based on the layout_type parameter
    if layout_type == "spring_layout":
        pos = nx.spring_layout(G)
    elif layout_type == "shell_layout":
        pos = nx.shell_layout(G)
    elif layout_type == "kamada_kawai_layout":
        pos = nx.kamada_kawai_layout(G)
    else:
        raise ValueError(f"Unknown layout type: {layout_type}")

    # Calculate modularity
    modularity_score = calculate_modularity(G, best_partition)
    print(f"Modularity: {modularity_score}")

    # Prepare colors for communities
    unique_comms = np.unique(list(best_partition.values()))
    comm_colors = plt.cm.tab20b(np.linspace(0, 1, len(unique_comms)))
    comm_color_dict = dict(zip(unique_comms, comm_colors))

    # Assign colors to nodes based on their community
    node_colors = [comm_color_dict[best_partition[i]] for i in G.nodes]

    # Plot the graph
    fig, ax = plt.subplots(1, 1, figsize=(7, 5), dpi=100)
    nx.draw(G, pos=pos, node_color=node_colors, with_labels=True, ax=ax)
    plt.show()

def vis_network_agg_spring(G, best_partition, layout1="shell_layout", iterations=1):
    """
    Visualize a network using an aggregated layout approach. The first layout is either 'shell_layout' or 
    'kamada_kawai_layout', and the second layout is always 'spring_layout' for a specified number of iterations.

    Parameters:
    G (networkx.Graph): The graph to visualize
    best_partition (dict): A partition of the graph nodes (community assignments)
    layout1 (str): The first layout algorithm to use, either 'shell_layout' or 'kamada_kawai_layout' (default is 'shell_layout')
    iterations (int): The number of iterations for the 'spring_layout' adjustment (default is 1)

    Returns:
    None: Displays the network graph
    """
    # Step 1: Choose and apply the first layout to get initial positions
    if layout1 == "shell_layout":
        pos = nx.shell_layout(G)
    elif layout1 == "kamada_kawai_layout":
        pos = nx.kamada_kawai_layout(G)
    else:
        raise ValueError(f"Unknown layout1 type: {layout1}. Choose either 'shell_layout' or 'kamada_kawai_layout'.")

    # Step 2: Apply the spring layout for the specified number of iterations, using the positions from the first layout
    pos = nx.spring_layout(G, pos=pos, iterations=iterations)

    # Step 3: Calculate modularity of the best partition
    modularity_score = calculate_modularity(G, best_partition)
    print(f"Best Modularity: {modularity_score}")

    # Step 4: Prepare colors for communities
    unique_comms = np.unique(list(best_partition.values()))
    comm_colors = plt.cm.tab20b(np.linspace(0, 1, len(unique_comms)))
    comm_color_dict = dict(zip(unique_comms, comm_colors))

    # Assign colors to nodes based on their community
    node_colors = [comm_color_dict[best_partition[i]] for i in G.nodes]

    # Step 5: Plot the graph with the aggregated positions
    fig, ax = plt.subplots(1, 1, figsize=(7, 5), dpi=100)
    nx.draw(G, pos=pos, node_color=node_colors, with_labels=True, ax=ax)
    plt.show()

def vis_network_partition_process(G, pos=None, method="girvan_newman", w=5.0, h=4.0, nrows=6, ncols=6, iterations_limit=None):
    """
    Visualize the partitioning process of a network using the Girvan-Newman algorithm.

    Parameters:
    G (networkx.Graph): The input graph
    pos (dict or None): Positions for the nodes in the graph. If None, default spring_layout will be used.
    method (str): Only "girvan_newman" is supported.
    w (float): Width of each subplot
    h (float): Height of each subplot
    nrows (int): Number of rows in the grid of subplots
    ncols (int): Number of columns in the grid of subplots
    iterations_limit (int): Limit the number of iterations to display. If None, display all iterations.

    Returns:
    None: Displays the partitioning process
    """
    # If no pos is provided, use spring_layout
    if pos is None:
        pos = nx.spring_layout(G)

    tups = list(it.product(range(nrows), range(ncols)))

    fig, ax = plt.subplots(nrows, ncols, figsize=(w * ncols, h * nrows), dpi=150)
    plt.subplots_adjust(wspace=0.2, hspace=0.4)

    best_partition = {i: i for i in G.nodes()}
    best_modularity = 0
    mods = [0.0]

    # Girvan-Newman algorithm (iterative)
    gn = list(nx.community.girvan_newman(G))
    iteration_count = len(gn) if iterations_limit is None else min(len(gn), iterations_limit)

    for ii in range(iteration_count):
        gn_i = gn[ii]
        part_i = {i: 0 for i in G.nodes()}
        node_comms_i = list(gn_i)
        ncomms_i = list(range(len(node_comms_i)))
        for ix, p_i in enumerate(gn_i):
            for v_i in p_i:
                part_i[v_i] = ncomms_i[ix]

        mod_i = calculate_modularity(G, part_i)
        mods.append(mod_i)
        if mod_i > best_modularity:
            best_partition = part_i.copy()
            best_modularity = mod_i

        unique_comms = np.unique(list(part_i.values()))
        comm_colors = plt.cm.tab20b(np.linspace(0, 1, len(unique_comms)))
        comm_color_dict = dict(zip(unique_comms, comm_colors))

        node_colors = [comm_color_dict[part_i[i]] for i in G.nodes]
        nx.draw(G, pos, node_color=node_colors, node_size=150, ax=ax[tups[ii + 3]])

        ax[tups[ii + 3]].set_title('Iteration: %i; Modularity: %.4f' % (ii + 1, mod_i), fontsize='x-large')

    # Highlight best iteration
    ax[tups[np.argmax(mods) + 3]].set_title('Iteration: %i; Modularity: %.4f' % (np.argmax(mods) + 1, best_modularity),
                                            fontsize='x-large', fontweight='bold')

    # Set description and modularity plot
    ax[tups[0]].text(0.5, 0.5, 'Illustration of\nGirvan-Newman\napproach', ha='center', va='center', fontsize='xx-large')
    ax[tups[0]].set_xlim(0, 1)
    ax[tups[0]].set_ylim(0, 1)
    ax[tups[0]].set_axis_off()

    # Plot modularity over iterations
    ax[tups[1]].plot(mods, lw=2, color='.2')
    ax[tups[1]].set_xlabel('Partition ID', fontsize='x-large')
    ax[tups[1]].set_ylabel('Modularity', fontsize='x-large')

    # Plot initial state
    ax[tups[2]].set_title('Iteration: %i; Modularity: %.4f' % (0, 0.0), fontsize='x-large')
    nx.draw(G, pos, node_color='.5', node_size=150, ax=ax[tups[2]])
    ax[tups[2]].set_axis_off()

    plt.show()
