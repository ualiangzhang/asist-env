from environment import MapParser
import matplotlib.pyplot as plt
import matplotlib.animation
import pandas as pd
from pathlib import Path
import networkx as nx
from graph import RandomGraphGenerator
from graph.Nodes import NodeType
from environment import AsistEnvGym
import json

# pos = nx.spring_layout(graph, k=0.9, iterations=3, pos=pos, fixed=fix, weight=3)

def plot_graph(graph, save=None, pop_out=False):
    if pop_out:
        matplotlib.use("TkAgg")
    # Get position
    pos, fix = graph.better_layout(expand_iteration=3)
    pos = graph.flip_z(pos)
    pos = graph.clockwise90(pos)
    weight_labels = nx.get_edge_attributes(graph,'weight')
    plt.figure(figsize=(18,27))
    color_map = graph.better_color()

    nx.draw_networkx(graph, pos, with_labels=True, node_color=color_map)
    # nx.draw_networkx_edge_labels(graph, pos, edge_labels=weight_labels)

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
    print(len(animation_sequence))
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
    ani = matplotlib.animation.FuncAnimation(fig, update, frames=animation_sequence, interval=130)
    # plt.show()
    ani.save('animation_processed_04_130.mp4')

def animate_graph_training(animation_sequence, portal_data, room_data, victim_data, with_save=False):
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
        curr_node = animation_frame[0]
        if graph[curr_node].type == NodeType.Victim:
            cost, reward = graph.triage(graph[curr_node])

        color_map = graph.better_color(curr_node)
        nx.draw(graph, pos, with_labels=False, node_color=color_map, node_size=50,
                font_size=7, width=0.5)
        # nx.draw_networkx_edge_labels(graph, pos, edge_labels=weight_labels, font_size=7)
        ax.set_title(f"Time: {animation_frame[1]:.2f}  Score: {animation_frame[2]}")
        # ax.set_title("Steps: " + str(animation_frame[0]))

    fig, ax = plt.subplots(figsize=(6,6))
    fig.subplots_adjust(left=0, bottom=0, right=1, top=0.9, wspace=None, hspace=None)
    ani = matplotlib.animation.FuncAnimation(fig, update, frames=animation_sequence, interval=200, repeat=False)
    if not with_save:
        plt.show()
    else:
        ani.save('evaluation_20.mp4')
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
    # G = MapParser.no_victim_map(portal_data, room_data)
    # no_victim_rooms = {"achl", "alha", "alhb", "ach", "arha", "arhb", "as"}
    # G = RandomGraphGenerator.add_random_victims(G, no_victim_rooms)


    with open('data/json/Falcon_v1.0_Easy_sm_clean.json') as f:
        data = json.load(f)
    # env = AsistEnvGym(portal_data, room_data, victim_data, "as", random_victim=False)

    graph = MapParser.parse_json_map_data_new_format(data)

    plot_graph(graph, save="Easy_New")
    # animate_graph()

    # plot_random_graph()

