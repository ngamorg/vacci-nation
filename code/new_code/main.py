import networkx as nx
import numpy as np
from small_world_network import SmallWorldNetwork

from agent import Agent, Health, Group, GroupBehavior


n = 100
group_percentages = [0.7, 0.3]
k = 4
change_edge_percentage = 0.2
alpha = 0.2

groups = [Group.TRUSTER, Group.SKEPTICAL]
group_behaviours = [GroupBehavior(Group.TRUSTER), GroupBehavior(Group.SKEPTICAL)]


age_mu = 40
age_sigma = 15

lim_init_infected = [0.02, 0.02]
lim_init_vacci = [0.07, 0.02]

agents = list()


def setup():
    global agent

    G = SmallWorldNetwork(n, group_percentages, alpha, k, change_edge_percentage)

    # Create Agent for every node
    for i in G.network.nodes:
        age = np.random.normal(age_mu, age_sigma)

        group_id = G.group_colors[i]
        group = groups[group_id]

        status = Health.SUSCEPTIBLE

        init_status_p = np.random.uniform(0.0, 1.0)

        if init_status_p <= lim_init_infected[group_id]:
            status = Health.INFECTED
        elif init_status_p <= lim_init_vacci[group_id]:
            status = Health.VACCINATED

        agent = Agent(i, age, status, group)
        agents.append(agent)

    return G


def simulate(world : SmallWorldNetwork, group_behaviours, agents):
    for i in world.network.nodes:
        agents[i].run(group_behaviours, world.network.neighbors(i), agents)

    for i in world.network.nodes:
        agents[i].update()


def export(net, agents, v):
    # Color vertices
    for i in net.nodes:
        if agents[i].get_health_status() == Health.SUSCEPTIBLE:
            net.nodes[i]['viz'] = {'color': {'r': 0, 'g': 255, 'b': 0, 'a': 1.0}}
        if agents[i].get_health_status() == Health.INFECTED:
            net.nodes[i]['viz'] = {'color': {'r': 255, 'g': 0, 'b': 0, 'a': 1.0}}
        if agents[i].get_health_status() == Health.RECOVERED:
            net.nodes[i]['viz'] = {'color': {'r': 0, 'g': 0, 'b': 0, 'a': 1.0}}
        if agents[i].get_health_status() == Health.VACCINATED:
            net.nodes[i]['viz'] = {'color': {'r': 0, 'g': 0, 'b': 255, 'a': 1.0}}

        # Color edges
        for e in net.edges:
            net.edges[e]['viz'] = {'color': {'r': 220, 'g': 220, 'b': 220, 'a': 1.0}}

        nx.write_gexf(net, "export/export-"+str(v)+".gexf")


timesteps = 50
save_after = 10

world = setup()
nx.write_gexf(world.network, "export/export-groups.gexf")

for i in range(timesteps):
    print("simulated " + str(i))
    # save?
    if i % save_after == 0:
        export(world.network, agents, i)

    simulate(world, group_behaviours, agents)


print("Done")
