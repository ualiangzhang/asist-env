from environment import MapParser
import matplotlib.pyplot as plt
import matplotlib.animation
import pandas as pd
from pathlib import Path
import networkx as nx
from graph import RandomGraphGenerator
from graph.Nodes import NodeType

# pos = nx.spring_layout(graph, k=0.9, iterations=3, pos=pos, fixed=fix, weight=3)

def plot_graph(save=None):
    graph = MapParser.parse_map_data(portal_data, room_data, victim_data)
    # Get position
    pos, fix = graph.better_layout()
    pos = graph.flip_z(pos)
    pos = graph.clockwise90(pos)
    weight_labels = nx.get_edge_attributes(graph,'weight')
    plt.figure(figsize=(15,15))
    color_map = graph.better_color()
    nx.draw(graph, pos, with_labels=True, node_color=color_map, edge_labels=weight_labels)
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=weight_labels)

    if save is None:
        plt.show()
    else:
        plt.savefig(save + ".png")

def plot_random_graph():
    plt.figure(figsize=(8,8))
    graph = RandomGraphGenerator.generate_random_graph(5, (2,8), (0,2), (0,1))
    pos = nx.kamada_kawai_layout(graph)
    weight_labels = nx.get_edge_attributes(graph,'weight')
    color_map = graph.better_color()
    nx.draw(graph, pos, with_labels=True, node_color=color_map, edge_labels=weight_labels)
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=weight_labels)
    plt.show()


def animate_graph():
    animation_sequence = pd.read_csv(r"data\animation_sequence_processed_04.csv").values.tolist()
    # animation_sequence = animation_sequence[:30]
    # print(animation_sequence)
    graph = MapParser.parse_map_data(portal_data, room_data, victim_data)
    # Get position
    pos, fix = graph.better_layout()
    pos = graph.flip_z(pos)
    pos = graph.clockwise90(pos)
    weight_labels = nx.get_edge_attributes(graph,'weight')

    # Animation update function
    def update(animation_sequence):
        ax.clear()
        curr_node = animation_sequence[1]
        if graph[curr_node].type == NodeType.Victim:
            cost, reward = graph.triage(graph[curr_node])
        if animation_sequence[0] > 300:
            graph.kill_all_yellow_victims()
        print(animation_sequence[0])
        color_map = graph.better_color(curr_node)
        nx.draw(graph, pos, with_labels=True, node_color=color_map, node_size=50, edge_labels=weight_labels,
                font_size=7, width=0.5)
        nx.draw_networkx_edge_labels(graph, pos, edge_labels=weight_labels, font_size=7)
        ax.set_title("Time: " + str(animation_sequence[0]) + "  Score: " + str(animation_sequence[2]))

    fig, ax = plt.subplots(figsize=(10,10))
    fig.subplots_adjust(left=0, bottom=0, right=1, top=0.9, wspace=None, hspace=None)
    ani = matplotlib.animation.FuncAnimation(fig, update, frames=animation_sequence, interval=300)
    # plt.show()
    ani.save('animation_processed_04.mp4')

def animate_graph_training(animation_sequence, portal_data, room_data, victim_data):
    # matplotlib.use("Qt5Agg")
    matplotlib.use("TkAgg")
    graph = MapParser.parse_map_data(portal_data, room_data, victim_data)
    # Get position
    pos, fix = graph.better_layout()
    pos = graph.flip_z(pos)
    pos = graph.clockwise90(pos)
    # weight_labels = nx.get_edge_attributes(graph,'weight')

    # Animation update function
    def update(animation_frame):
        # if animation_frame[0] == len(animation_sequence) - 1:
        #     plt.close(fig)

        ax.clear()
        curr_node = animation_frame
        if graph[curr_node].type == NodeType.Victim:
            cost, reward = graph.triage(graph[curr_node])

        color_map = graph.better_color(curr_node)
        nx.draw(graph, pos, with_labels=False, node_color=color_map, node_size=50,
                font_size=7, width=0.5)
        # nx.draw_networkx_edge_labels(graph, pos, edge_labels=weight_labels, font_size=7)
        # ax.set_title("Steps: " + str(animation_frame[0]) + "  Score: " + str(animation_frame[2]))
        # ax.set_title("Steps: " + str(animation_frame[0]))

    fig, ax = plt.subplots(figsize=(6,6))
    fig.subplots_adjust(left=0, bottom=0, right=1, top=0.9, wspace=None, hspace=None)
    ani = matplotlib.animation.FuncAnimation(fig, update, frames=animation_sequence, interval=10, repeat=False)
    plt.show()
    # del ani
    # del fig


if __name__ == '__main__':
    # =================================
    # Data Load Start
    # =================================
    data_folder = Path("data")

    portals_csv = data_folder / "sparky_portals.csv"
    rooms_csv = data_folder / "sparky_rooms.csv"
    victims_csv = data_folder / "sparky_victims.csv"

    portal_data = pd.read_csv(portals_csv)
    room_data = pd.read_csv(rooms_csv)
    victim_data = pd.read_csv(victims_csv)
    # =================================
    # Data Load End
    # =================================

    plot_graph(save="graph_newcolor")
    # animate_graph()

    # plot_random_graph()

