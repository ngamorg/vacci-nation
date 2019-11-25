import random
import networkx as nx


class SmallWorldNetwork:

    """
    Creates a graph with num_nodes nodes and splits them up into num_groups = |group_percentage|
    watts_strogatz_graph(num_nodes_group, k, p, seed=None) graphs  and then then adds to every pair of distinct groups
    i.e. groups i and j i != j, a * (|i| + |j|) edges.
    """
    def __init__(self, num_nodes, group_percentages, a, k, p):
        num_groups = len(group_percentages)

        """
        groups contains all watts_strogatz_graph graphs relating to group 0, ..., (num_groups - 1)
        """
        self.groups = []
        self.groups_translation = []
        self.group_colors = []
        self.network = nx.Graph()

        self.create_groups(group_percentages, k, num_groups, num_nodes, p)
        self.combine_groups(num_groups)
        self.connect_groups(a, num_groups)

    def connect_groups(self, a, num_groups):
        """
        Add edges between all groups i, j and  i != j, where the number of edges is a * |group i| * |group j|
        """
        for i in range(0, num_groups):
            for j in range(i+1, num_groups):
                size_i = len(self.groups[i])
                size_j = len(self.groups[j])
                num_add_edges = int(a * (size_i + size_j))

                for k in range(0, num_add_edges):
                    node_i = random.randint(0, size_i - 1) + self.groups_translation[i]
                    node_j = random.randint(0, size_j - 1) + self.groups_translation[j]

                    self.network.add_edge(node_i, node_j)

    def combine_groups(self, num_groups):

        colors = [
            {'r': 255, 'g': 0, 'b': 0, 'a': 1.0},
            {'r': 0, 'g': 255, 'b': 0, 'a': 1.0},
            {'r': 0, 'g': 0, 'b': 255, 'a': 1.0},
            {'r': 122, 'g': 0, 'b': 122, 'a': 1.0},
        ]

        """
        Add all the nodes and edges of every group to a single graph. groups_stranslation will contain the translations
        that are needed to convert from nodes of group i to the whole network. Also set the group_colors st.
        group_colors[k] colors node k, st. all nodes in the same group have the same color.
        """
        k = 0
        self.groups_translation.append(0)

        for i in range(0, num_groups):
            group = self.groups[i]
            new_group = nx.Graph()
            for node in group.nodes:
                self.network.add_node(node + k)
                new_group.add_node(node + k)
                self.group_colors.append(i)
                self.network.nodes[node+k]['viz'] = {'color': colors[i]}
            for edge in group.edges:
                self.network.add_edge(edge[0] + k, edge[1] + k)
                new_group.add_edge(edge[0] + k, edge[1] + k)
            k = k + len(group.nodes)
            self.groups[i] = new_group
            self.groups_translation.append(k)

    def create_groups(self, group_percentages, k, num_groups, num_nodes, p):
        """
         creates for every group a watts_strogatz_graph graph and stores it in groups.
        """
        for i in range(0, num_groups):
            num_nodes_group = int(num_nodes * group_percentages[i])
            self.groups.append(nx.watts_strogatz_graph(num_nodes_group, k, p, seed=None))