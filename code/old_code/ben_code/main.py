import networkx as nx
import small_world_network as swn
import agent
import matplotlib.pyplot as plt
import random
from matplotlib.animation import FuncAnimation

"""
initial values for network
"""
expected_num_nodes = 100
group_percentages = [0.1, 0.4, 0.5]

alpha = 0.05
neigh = 4
change_edge_percentage = 0.2

"""
initial values for simulation
"""

group_avg_inner_contacts = [0.05, 0.05, 1]
group_avg_outer_contacts = [0, 0, 0]
group_avg_vaccine_bias = [0.1, 0.2, 0.3]

initial_infected_percentage = 0.1

recuperation_prob = 0.1

num_seasons = 10
num_tick_per_season = 100

world = None
agents = None


def apply_recuperation():
    """
    look at every infected agent and heal them with probability recuperation_prob
    """
    for a in agents:
        if a.infected == 1:
            r = random.random()
            if r < recuperation_prob:
                a.infected = 0


def eval_infection():
    """
    iterate through all agents and if they are infected try to infect their neighbours (only if not infected)
    depending if their neighbour is in the same group or not different probs apply, i.e avg_inner_contacts
    and avg_outer_contacts
    """
    for a in agents:
        if a.infected == 1:
            for neighbour in world.network.neighbors(a.id):
                if agents[neighbour].infected == 0:
                    r = random.random()
                    a_group = world.group_colors[a.id]
                    if a_group == world.group_colors[neighbour]:
                        if r < group_avg_inner_contacts[a_group]:
                            agents[neighbour].infected_n = 1
                    else:
                        if r < group_avg_outer_contacts[a_group]:
                            agents[neighbour].infected_n = 1


def apply_infection():
    """
    iterates through all agents and if a.infected == 1 clear it and set a.infected = 1
    """
    for a in agents:
        if a.infected_n == 1:
            a.infected_n = 0
            a.infected = 1


def apply_vaccination():
    """
    TO DO
    """
    pass


def create_agents(world):
    """
    create agents
    """
    global num_nodes
    num_nodes = len(world.network.nodes)
    num_groups = len(world.groups)
    agents = []
    for i in range(0, num_nodes):
        agents.append(agent.Agent(i))
    return agents, num_nodes


def infected_global_percentage(agents):
    """
    returns #infected agents / #agents
    """
    infected = 0
    total = 0.0

    for agent in agents:
        total = total + 1
        if agent.infected == 1:
            count = count + 1


def infected_local_percentages(agents, world, depth):
    """
    returns #infected agents at most depth nodes away / #agents at most depth away
    """

    pass


def infect_population(agents, num_nodes):
    """
    assign initial infected population with probability  initial_infected_percentage
    """
    for i in range(0, num_nodes):
        r = random.random()
        if r < initial_infected_percentage:
            agents[i].infected = 1
        else:
            agents[i].infected = 0


def generate_infected_list(agents):
    """
    iterate through all agends and generate a list infected where agent[i].infected == 1 <=> infected[i] == 1, else 0
    """
    infected = []

    for i in range(0, len(agents)):
        infected.append(agents[i].infected)
    return infected


def draw_network(world, color, pos):
    """
    draw the current network to a plot with node and edge positions pos and colored with rule color, then show it.
    """
    for group in world.groups:
        nx.draw(group, pos)
        plt.show()
        print(group.nodes)

    nx.draw_networkx_edges(world.network, pos, edgelist=world.network.edges)
    nx.draw_networkx_nodes(world.network, pos, nodelist=world.network, node_color=color)
    plt.show()


"""
initialize
"""
world = swn.SmallWorldNetwork(expected_num_nodes, group_percentages, alpha, neigh, change_edge_percentage)
agents, num_nodes = create_agents(world)
infect_population(agents, num_nodes)

"""
start simulation
"""

fig = plt.figure()

pos = nx.spring_layout(world.network)


def time_stamp(n):
    """
    for FuncAnimation, applies a timestamp of the simulation. if new season starts, apply vaccination
    """
    print(n)
    if n % num_tick_per_season == 0:
        apply_vaccination()
    eval_infection()
    apply_recuperation()
    apply_infection()
    fig.clf()
    edges = nx.draw_networkx_edges(world.network, pos, edgelist=world.network.edges)
    nodes = nx.draw_networkx_nodes(world.network, pos, nodelist=world.network,
                                   node_color=generate_infected_list(agents))
    return nodes

"""
start animation and save it as netowrk.mp4, then display the network with respect to groupss
"""
ani = FuncAnimation(fig, time_stamp, frames=500, interval=100)
ani.save('network.mp4', fps=4, extra_args=['-vcodec', 'libx264'])
plt.show()
plt.close()

draw_network(world, world.group_colors, pos)
