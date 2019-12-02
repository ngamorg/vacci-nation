import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.lines import Line2D

from small_world_network import SmallWorldNetwork

from agent import Agent, Health, Group, GroupBehavior

n = 1000
#                    Trust Skept
group_percentages = [0.5, 0.5]
k = 8
change_edge_percentage = 0.2
alpha = 0.3

groups = [Group.TRUSTER, Group.SKEPTICAL]
group_behaviours = [GroupBehavior(Group.TRUSTER), GroupBehavior(Group.SKEPTICAL)]

age_mu = 40
age_sigma = 15

lim_init_infected = [0.005, 0.005]
lim_init_vacci = [0.005, 0.005]

agents = list()

depth = 1

Agent.beta = 0.05

frames = 100
fps = 4

def setup():
    global agent

    G = SmallWorldNetwork(n, group_percentages, alpha, k, change_edge_percentage, depth)

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


def simulate(world: SmallWorldNetwork, group_behaviours, agents):
    for i in world.network.nodes:
        agents[i].run(group_behaviours, world.network.neighbors(i), world.depth_neighbors[i], agents)

    for i in world.network.nodes:
        agents[i].update()


def count_status(agents):
    """
    counts all health states in the network
    :param agents:
    :return:
    """
    num_inf = 0
    num_sus = 0
    num_rec = 0
    num_vac = 0
    num_vacT = 0
    num_vacS = 0

    for agent in agents:
        if agent.get_health_status() == Health.INFECTED:
            num_inf += 1
        if agent.get_health_status() == Health.RECOVERED:
            num_rec += 1
        if agent.get_health_status() == Health.VACCINATED:
            if agent._group == Group.TRUSTER:
                num_vacT += 1
            if agent._group == Group.SKEPTICAL:
                num_vacS += 1
            num_vac += 1
        if agent.get_health_status() == Health.SUSCEPTIBLE:
            num_sus += 1

    Agent.num_inf = num_inf
    Agent.num_sus = num_sus
    Agent.num_vac = num_vac
    Agent.num_rec = num_rec
    Agent.num_vacT = num_vacT
    Agent.num_vacS = num_vacS


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

        nx.write_gexf(net, "export/export-" + str(v) + ".gexf")


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
    """
    :param health:
    :return: num(health)
    """
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


def health_list_to_color(health_list):
    """
    convertss the health_list which is a list of integers to a list of strings, where the strings represent colors
    SUSCEPTIBLE <-> yellow
    INFECTED <->  red
    RECOVERED <-> green
    VACCINATED <-> navy
    """
    color_health_list = []
    colors = ["yellow", "red", "green", "navy"]
    for i in range(0, len(health_list)):
        color_health_list.append(colors[health_list[i]])
    return color_health_list


def split_groups(nodes, group_list, health_color):
    """
    Splits the list of nodes and health color into two different lists coressponding to their groups.
    :param nodes:
    :param group_list:
    :param health_color:
    :return: nodes0, nodes1, healh_color0, health_color1
    """
    health_color0 = []
    health_color1 = []

    nodes0 = []
    nodes1 = []
    for i in nodes:
        if group_list[i] % 2 == 0:
            health_color0.append(health_color[i])
            nodes0.append(i)
        else:
            health_color1.append(health_color[i])
            nodes1.append(i)

    return nodes0, nodes1, health_color0, health_color1


def time_stamp(iteration):
    """

    :param iteration:
    :return: void
    """
    print(iteration)

    global fig
    simulate(world, group_behaviours, agents)
    #clears figure


    fig.clf()

    n0, n1, h0, h1 = split_groups(world.network, world.group_colors, generate_health_list(agents))

    edges = nx.draw_networkx_edges(world.network, pos, width=0.1, edgelist=world.network.edges)

    ch0 = health_list_to_color(h0)
    ch1 = health_list_to_color(h1)
    nodes0 = nx.draw_networkx_nodes(n0, pos, node_size=7, node_shape='^', nodelist=n0,
                                    node_color=ch0, label='Trusters')
    nodes1 = nx.draw_networkx_nodes(n1, pos, node_size=7, nodelist=n1, node_color=ch1, label='Skepticals')
    plt.legend(scatterpoints=1)
    legend_entries = [Line2D([0], [0], color="navy", marker='^', lw=0),
                      Line2D([0], [0], color="navy", marker='o', lw=0),
                      Line2D([0], [0], color="yellow", lw=2),
                      Line2D([0], [0], color="red", lw=2),
                      Line2D([0], [0], color="green", lw=2),
                      Line2D([0], [0], color="navy", lw=2)]

    plt.legend(legend_entries, ["Truster", "Skeptical", "Susceptible", "Infected", "Recovered", "Vaccinated"])


    i = iteration
    count_status(agents)
    plot[i]['sus'] = Agent.num_sus
    plot[i]['inf'] = Agent.num_inf
    plot[i]['rec'] = Agent.num_rec
    plot[i]['vac'] = Agent.num_vac
    plot[i]['vacT'] = Agent.num_vacT
    plot[i]['vacS'] = Agent.num_vacS
    plot[i]['recvac'] = Agent.num_rec + Agent.num_vac
    return world.network

def group_neighbors():
    pass


def simulate_animation():
    """
    Create a FuncAnimation which draws on fig, calls the function time_stamp every iteration to update the simulation.
    :return: void
    """
    global fig
    ani = FuncAnimation(fig, time_stamp, frames=frames)
    ani.save('network.mp4', fps=fps, extra_args=['-vcodec', 'libx264'])

    plt.close()
    fig2 = plt.figure()
    fig2.clf()
    ax = fig2.add_subplot(111, axisbelow=True)
    print(plot)
    ax.plot(range(frames), [elem['sus'] for elem in plot], 'yellow', lw=1.5, label="Susceptible")
    ax.plot(range(frames), [elem['vac'] for elem in plot], 'navy', lw=1.5, label="Vaccinated")
    ax.plot(range(frames), [elem['vacT'] for elem in plot], 'skyblue', lw=1.5, label="VaccinatedT")
    ax.plot(range(frames), [elem['vacS'] for elem in plot], 'cyan', lw=1.5, label="VaccinatedS")
    ax.plot(range(frames), [elem['rec'] for elem in plot], 'green', lw=1.5, label="Recovered")
    ax.plot(range(frames), [elem['inf'] for elem in plot], 'red', lw=1.5, label="Infected")
    ax.plot(range(frames), [elem['recvac'] for elem in plot], 'darkgrey', lw=1.5, label="Recovered or Vaccinated")
    ax.set_ylim(0, world.network.number_of_nodes())
    ax.set_xlim(0, frames)
    plt.legend()
    plt.show()


world = setup()
fig = plt.figure(dpi=300)
plot = [{} for i in range(frames)]

#compute the position of all nodes in the network
pos = nx.spring_layout(world.network)

#start the animation
simulate_animation()

exit()
