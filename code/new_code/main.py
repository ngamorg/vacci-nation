import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from small_world_network import SmallWorldNetwork

from agent import Agent, Health, Group, GroupBehavior


n = 1000
group_percentages = [0.6, 0.4]
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


def simulate_export():
    timesteps = 120
    save_after = 120

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
        # if i % save_after == 0:
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


def health2num(health):
    if health == agent._health.SUSCEPTIBLE:
        return 0
    if health == agent._health.INFECTED:
        return 1
    if health == agent._health.RECOVERED:
        return 2
    if health == agent._health.VACCINATED:
        return 3


def generate_health_list(agents):
    """
    iterate through all agends and generate a list infected where agent[i].infected == 1 <=> infected[i] == 1, else 0
    """
    infected = []

    for i in range(0, len(agents)):
        infected.append(health2num(agents[i]._health))
    return infected


def split_groups(nodes, group_list, health_color):
    health_color0 = []
    health_color1 = []

    nodes0 = []
    nodes1 = []
    for i in nodes:
        if group_list[i]%2 == 0:
            health_color0.append(health_color[i])
            nodes0.append(i)
        else:
            health_color1.append(health_color[i])
            nodes1.append(i)

    return nodes0, nodes1, health_color0, health_color1


def time_stamp(iteration):
    print(iteration)

    simulate(world, group_behaviours, agents)
    fig.clf()

    n0, n1, h0, h1  = split_groups(world.network, world.group_colors, generate_health_list(agents))

    edges = nx.draw_networkx_edges(world.network, pos,width = 0.1, edgelist=world.network.edges)
    
    
    nodes0 = nx.draw_networkx_nodes(n0, pos,node_size=7, node_shape='^',  nodelist=n0,
                                   node_color=h0, label='Trusters')
    nodes1 = nx.draw_networkx_nodes(n1, pos, node_size=7, nodelist=n1, node_color=h1, label='Skepticals')
    plt.legend(scatterpoints=1) 
    return world.network


def simulate_animation():
    ani = FuncAnimation(fig, time_stamp, frames=100, interval=100)
    ani.save('network.mp4', fps=4, extra_args=['-vcodec', 'libx264'])


world = setup()
fig = plt.figure(dpi = 300)
pos = nx.spring_layout(world.network)

simulate_animation()

exit()
