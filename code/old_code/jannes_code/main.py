import networkx as nx
import scipy.stats
import matplotlib.pyplot as plt

from agent import Agent
from network import Network
from random import randrange

import copy


def setup():
    # Graph parameters
    n = 1000
    m = 3
    k = 3
    p = 0.15

    # Epidemics parameters
    p_vacci = 0.02
    p_infected = 0.05

    # Small world graph to simulate society
    #G = nx.watts_strogatz_graph(n, k, p)
    G = nx.barabasi_albert_graph(n, m)
    agents = list()

    # Create agent for each vertex
    for i in range(n):
        ag = Agent()
        agents.append(ag)

    # Initial sick people

    # Initially recovered / vaccinated
    to_be_vacci = p_vacci*n
    to_be_infected = p_infected*n

    infected = 0
    vaccinated = 0

    while infected < to_be_infected:
        success = False
        while not success:
            r = randrange(n)
            if agents[r].is_healthy():
                agents[r].get_infected()
                success = True
        infected += 1

    while vaccinated < to_be_vacci:
        success = False
        while not success:
            r = randrange(n)
            if agents[r].is_healthy():
                agents[r].recover()
                success = True
        vaccinated += 1

    print("init infected: " + str(infected))
    print("init vaccinated: " + str(vaccinated))
    print("init susceptible: " + str(n-infected-vaccinated))

    Agent.num_inf = infected
    Agent.num_rec = vaccinated
    Agent.num_sus = n - infected - vaccinated

    # return network
    net = Network(G, agents)
    print("Setup complete")
    return net


def simulate(net):
    # Infection parameters
    infection_mu = 0.15
    infection_sigma = 0.07

    # Recover parameters
    recover_mu = 0.05
    recover_sigma = 0.03

    snap_net = copy.deepcopy(net)

    for v in snap_net.graph.nodes:
        # skip this node if recovered
        if snap_net.agents[v].is_recovered():
            continue

        # get neighbors
        neighbors = snap_net.graph.neighbors(v)
        for n in neighbors:
            # neighbor infected
            if snap_net.agents[n].is_infected():
                infection_prop = scipy.stats.norm.rvs(loc=infection_mu, scale=infection_sigma)
                r = randrange(100)
                if infection_prop*100 > r:
                    net.agents[v].get_infected()
                    break

        # recover or vaccinate?
        recover_prop = scipy.stats.norm.rvs(loc=recover_mu, scale=recover_sigma)
        if (snap_net.agents[v].is_infected() or snap_net.agents[v].is_healthy()) and recover_prop*100 > randrange(100):
            if snap_net.agents[v].is_infected():
                net.agents[v].heal_without_immunity()
            else:
                net.agents[v].recover()
    return net


def export(net, v):
    # Color vertices
    for i in range(net.graph.number_of_nodes()):
        if net.agents[i].is_healthy():
            net.graph.nodes[i]['viz'] = {'color': {'r': 0, 'g': 255, 'b': 0, 'a': 1.0}}
        if net.agents[i].is_infected():
            net.graph.nodes[i]['viz'] = {'color': {'r': 255, 'g': 0, 'b': 0, 'a': 1.0}}
        if net.agents[i].is_recovered():
            net.graph.nodes[i]['viz'] = {'color': {'r': 0, 'g': 0, 'b': 255, 'a': 1.0}}

    # Color edges
    for e in net.graph.edges:
        net.graph.edges[e]['viz'] = {'color': {'r': 220, 'g': 220, 'b': 220, 'a': 1.0}}

    nx.write_gexf(net.graph, "export/export-"+str(v)+".gexf")


timesteps = 100
save_after = 10

network = setup()

plot = [{} for i in range(timesteps)]
plot[0]['sus'] = Agent.num_sus
plot[0]['inf'] = Agent.num_inf
plot[0]['rec'] = Agent.num_rec

# initial export
export(network, 0)

for i in range(timesteps):
    network = simulate(network)
    print("simulated " + str(i))
    print("Healthy: " + str(Agent.num_sus) + " Infected: " + str(Agent.num_inf) + " Recovered: " + str(Agent.num_rec))

    # save?
    if i % save_after == 0:
        export(network, i)

    # plot
    plot[i]['sus'] = Agent.num_sus
    plot[i]['inf'] = Agent.num_inf
    plot[i]['rec'] = Agent.num_rec

export(network, timesteps)

fig = plt.figure()
ax = fig.add_subplot(111, axisbelow=True)
ax.plot(range(timesteps), [elem['sus'] for elem in plot], 'green', lw=1.5, label="Susceptible")
ax.plot(range(timesteps), [elem['rec'] for elem in plot], 'blue', lw=1.5, label="Recovered / Vaccinated")
ax.plot(range(timesteps), [elem['inf'] for elem in plot], 'red', lw=1.5, label="Infected")
ax.set_ylim(0, len(network.agents))
ax.set_xlim(0, timesteps)
plt.show()
