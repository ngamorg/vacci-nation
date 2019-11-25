import networkx as nx
import numpy as np
import scipy.stats
import matplotlib.pyplot as plt

from small_world_network import SmallWorldNetwork

from agent import Agent, Health, Group, GroupBehavior


n = 1000
group_percentages = [0.4, 0.15, 0.3, 0.15]
k = 4
change_edge_percentage = 0.2
alpha = 0.2

groups = [Group.TRUSTER, Group.SKEPTICAL]
group_behaviours = [GroupBehavior(Group.TRUSTER), GroupBehavior(Group.SKEPTICAL)]


age_mu = 40
age_sigma = 15

lim_init_infected = [0.01, 0.01]
lim_init_vacci = [0.06, 0.01]

agents = list()


def setup():
    global agent

    G = SmallWorldNetwork(n, group_percentages, alpha, k, change_edge_percentage)

    # Create Agent for every node
    for i in G.network.nodes:
        age = np.random.normal(age_mu, age_sigma)

        group_id = G.group_colors[i] % 2
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


def count_status(agents):
    num_inf = 0
    num_sus = 0
    num_rec = 0
    num_vac = 0

    for agent in agents:
        if agent.get_health_status() == Health.INFECTED:
            num_inf += 1
        if agent.get_health_status() == Health.RECOVERED:
            num_rec += 1
        if agent.get_health_status() == Health.VACCINATED:
            num_vac += 1
        if agent.get_health_status() == Health.SUSCEPTIBLE:
            num_sus += 1

    Agent.num_inf = num_inf
    Agent.num_sus = num_sus
    Agent.num_vac = num_vac
    Agent.num_rec = num_rec


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


timesteps = 120
save_after = 120

world = setup()
count_status(agents)

plot = [{} for i in range(timesteps)]
plot[0]['sus'] = Agent.num_sus
plot[0]['inf'] = Agent.num_inf
plot[0]['rec'] = Agent.num_rec
plot[0]['vac'] = Agent.num_vac
plot[0]['recvac'] = Agent.num_vac + Agent.num_rec


nx.write_gexf(world.network, "export/export-groups.gexf")

for i in range(timesteps):
    print("simulated " + str(i))

    # save?
    #if i % save_after == 0:
    #    export(world.network, agents, i)

    simulate(world, group_behaviours, agents)
    count_status(agents)
    # plot
    plot[i]['sus'] = Agent.num_sus
    plot[i]['inf'] = Agent.num_inf
    plot[i]['rec'] = Agent.num_rec
    plot[i]['vac'] = Agent.num_vac
    plot[i]['recvac'] = Agent.num_rec + Agent.num_vac


fig = plt.figure()
ax = fig.add_subplot(111, axisbelow=True)
ax.plot(range(timesteps), [elem['sus'] for elem in plot], 'green', lw=1.5, label="Susceptible")
ax.plot(range(timesteps), [elem['vac'] for elem in plot], 'blue', lw=1.5, label="Vaccinated")
ax.plot(range(timesteps), [elem['rec'] for elem in plot], 'orange', lw=1.5, label="Recovered")
ax.plot(range(timesteps), [elem['inf'] for elem in plot], 'red', lw=1.5, label="Infected")
ax.plot(range(timesteps), [elem['recvac'] for elem in plot], 'darkgrey', lw=1.5, label="Recovered or Vaccinated")
ax.set_ylim(0, world.network.number_of_nodes())
ax.set_xlim(0, timesteps)
plt.show()

print("Done")
exit()
