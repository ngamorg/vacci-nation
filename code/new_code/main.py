import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.lines import Line2D

from enum import Enum

from small_world_network import SmallWorldNetwork

from agent import Agent, Health, Group, GroupBehavior

class PlotMode(Enum):
    # generates a mp4 and a plot with all (sub) health states
    MP4PLOT = 0
    # same as mp4plot but without mp4
    ONLYPLOT = 1
    # plots the average vaccination amount with different group percentages over multiple runs against each other
    VACCIPLOT = 2

"""
START changable variables
"""

# define what the output should look like
mode = PlotMode.VACCIPLOT
# expected number of nodes of the network on which the simulation runs on
n = 1000

# percentage of Trusters and Skepticals in the network
#                   Trust Skept
group_percentages = [0.5, 0.5]

# number of initial neighbors when creating a group graph / watts_strogatz_graph
k = 8

# probability for every edge that it is relinked (in a group graph)
change_edge_percentage = 0.2

# number of edges that are added between two different groups i, j is alpha * ([number of nodes in i] + [number of nodes in j])
alpha = 0.05

# how far agents look into the future when deciding to vaccinate (days)
Agent.T = 5

# same length as group_percentages, define the group of every initial graph
groups = [Group.TRUSTER, Group.SKEPTICAL]
# same length as group_percentages, define the believes of every group
group_behaviours = [GroupBehavior(Group.TRUSTER), GroupBehavior(Group.SKEPTICAL)]

# initially infected
#                   Trust   Skept
lim_init_infected = [0.005, 0.005]

# initially vaccinated
#                 Trust  Skept
lim_init_vacci = [0.005, 0.005]


# change the depth of view the agents use to estimate their chance of getting infected, 1 => direct neighbors, 2 => neighbors of neighbors
depth = 1

# infection rate / probability that a person infects its neighbor
Agent.beta = 0.05

# number of iterations of the simulation
frames = 100

# frames per second of the simulation
fps = 4

"""
END changable variables
"""

agents = list()

age_mu = 40
age_sigma = 15

def setup():
    global agents
    agents = []
    print
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
    num_infT = 0
    num_infS = 0

    for agent in agents:
        if agent.get_health_status() == Health.INFECTED:
            if agent._group == Group.TRUSTER:
                num_infT += 1
            if agent._group == Group.SKEPTICAL:
                num_infS += 1
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
    Agent.num_infT = num_infT
    Agent.num_infS = num_infS


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
    if health == Health.SUSCEPTIBLE:
        return 0
    if health == Health.INFECTED:
        return 1
    if health == Health.RECOVERED:
        return 2
    if health == Health.VACCINATED:
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
    #print(iteration)

    global fig, agents, plot, vacci_plot
    simulate(world, group_behaviours, agents)
    #clears figure

    if mode == PlotMode.MP4PLOT:
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
        plot[i]['infT'] = Agent.num_infT
        plot[i]['infS'] = Agent.num_infS
        plot[i]['recvac'] = Agent.num_rec + Agent.num_vac

    if mode == PlotMode.VACCIPLOT:
        i = iteration
        count_status(agents)
        vacci_plot[vacci_iteration][i] += Agent.num_vac
        vacci_plot_truster[vacci_iteration][i] += Agent.num_vacT


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
    if mode == PlotMode.MP4PLOT or mode == PlotMode.ONLYPLOT:
        fig2 = plt.figure()
        fig2.clf()
        ax = fig2.add_subplot(111, axisbelow=True)
        plt.title("SIVR")
        plt.ylabel("agents")
        plt.xlabel("iterations")
        print(plot)
        ax.plot(range(frames), [elem['sus'] for elem in plot], 'yellow', lw=1.5, label="Susceptible")
        ax.plot(range(frames), [elem['vac'] for elem in plot], 'navy', lw=1.5, label="Vaccinated")
        ax.plot(range(frames), [elem['vacT'] for elem in plot], 'skyblue', lw=1.5, label="Vaccinated Truster")
        ax.plot(range(frames), [elem['vacS'] for elem in plot], 'cyan', lw=1.5, label="Vaccinated Skeptical")
        ax.plot(range(frames), [elem['rec'] for elem in plot], 'green', lw=1.5, label="Recovered")
        ax.plot(range(frames), [elem['inf'] for elem in plot], 'red', lw=1.5, label="Infected")
        ax.plot(range(frames), [elem['infT'] for elem in plot], 'tomato', lw=1.5, label="Infected Truster")
        ax.plot(range(frames), [elem['infS'] for elem in plot], 'pink', lw=1.5, label="Infected Skeptical")
        ax.plot(range(frames), [elem['recvac'] for elem in plot], 'darkgrey', lw=1.5, label="Recovered or Vaccinated")
        ax.set_ylim(0, world.network.number_of_nodes())
        ax.set_xlim(0, frames)
        plt.legend()
        plt.show()


if mode == PlotMode.MP4PLOT or mode == PlotMode.ONLYPLOT:

    fig = plt.figure(dpi=300)

    world = setup()
    plot = [{} for i in range(frames)]

    # compute the position of all nodes in the network
    pos = nx.spring_layout(world.network)

    # start the animation
    simulate_animation()

if mode == PlotMode.VACCIPLOT:
    """
    plot the average vaccination levels of different group_percentages over tries_per_percentage against each other.
    only works for two groups, currently with Trusters as group one and Skepticals as the second group
    start with the percentages start for the first group and (1 - start) for the second
    then increment start by step and do the same as above, repeat aslong <= end
    """
    fig = plt.figure(dpi=300)
    plot = [{} for i in range(frames)]
    vacci_iteration = 0
    simulations_per_percentage = 20
    start = 0.1
    step = 0.2
    end = 0.9
    total_vacci_iterations = int((end - start) / step + 1)
    print(total_vacci_iterations)
    vacci_plot = [[0 for i in range(frames)] for i in range(total_vacci_iterations)]
    vacci_plot_truster = [[0 for i in range(frames)] for i in range(total_vacci_iterations)]

    """
    simulate all
    """
    for vacci_iteration in range(total_vacci_iterations):
        group_percentage_left = round(start + vacci_iteration * step, 1)
        print(str(group_percentage_left) + " Truster", vacci_iteration)
        group_percentages[0] = group_percentage_left
        group_percentages[1] = round(1 - group_percentage_left, 1)

        for try_iteration in range(simulations_per_percentage):
            print(str(group_percentage_left), "simulation:", try_iteration)
            world = setup()
            simulate_animation()

    vacci_colors = ["red", "yellow", "green", "aqua", "navy"]


    """
    average and plot both plots
    """
    fig3 = plt.figure()
    fig3.clf()
    ax = fig3.add_subplot(111, axisbelow=True)
    ax.set_ylim(0, world.network.number_of_nodes())
    ax.set_xlim(0, frames)
    plt.ylabel("vaccinated agents")
    plt.xlabel("iteration")
    plt.title("avg. vaccination over " + str(simulations_per_percentage) + " simulations with respect to different group percentages")

    tvac_div_by_svac = [0 for i in range(total_vacci_iterations)]

    for vacci_iteration in range(total_vacci_iterations):

        for i in range(frames):
            vacci_plot[vacci_iteration][i] /= simulations_per_percentage
            vacci_plot_truster[vacci_iteration][i] /= simulations_per_percentage

        tvac_div_by_svac[vacci_iteration] = vacci_plot_truster[vacci_iteration][frames - 1] / (vacci_plot[vacci_iteration][frames - 1] - vacci_plot_truster[vacci_iteration][frames - 1])

        group_percentage_left = round(start + vacci_iteration * step, 1)
        group_percentage_right = round(1 - group_percentage_left, 1)
        ax.plot(range(frames), vacci_plot[vacci_iteration], vacci_colors[vacci_iteration], lw=1.5, label=str(group_percentage_left) + " Truster - " + str(group_percentage_right) + " Skeptical" )

    plt.legend()
    plt.show()
    fig4 = plt.figure()

    ax = fig4.add_subplot(111, axisbelow=True)
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0, 30.0)
    plt.xlabel("truster p")
    plt.ylabel("#tvacc / #svacc")
    plt.title("vaccination ratio between trusters and skepticals")
    xvals = [(start + i * step) for i in range(total_vacci_iterations)]

    print(xvals)
    print(tvac_div_by_svac)

    ax.plot(xvals, tvac_div_by_svac, 'navy', lw=1.5, label="(#truster vaccinations) / (#skeptical vaccinations) with #truster = (p * #agents)")

    plt.legend()
    plt.show()


exit()
