from environment import MapParser
import matplotlib.pyplot as plt
import matplotlib.animation
import pandas as pd
from pathlib import Path
import networkx as nx
from graph import RandomGraphGenerator

# pos = nx.spring_layout(graph, k=0.9, iterations=3, pos=pos, fixed=fix, weight=3)

def plot_graph(graph, pos, weight_labels, save=None):
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


def animate_graph(graph, pos, weight_labels):
    matplotlib.use("TkAgg")
    # Animation update function
    def update(num):
        pos, fix = graph.better_layout()
        ax.clear()
        color_map = graph.better_color()
        nx.draw(graph, pos, with_labels=True, node_color=color_map, ax=ax, node_size=100, edge_labels=weight_labels)
        nx.draw_networkx_edge_labels(graph, pos, edge_labels=weight_labels, ax=ax)

        ax.set_xticks([])
        ax.set_yticks([])

    fig, ax = plt.subplots(figsize=(10,10))
    ani = matplotlib.animation.FuncAnimation(fig, update, frames=6, interval=1000)
    plt.show()


if __name__ == '__main__':
    # Get data
    data_folder = Path("data")

    portals_csv = data_folder / "sparky_portals_Jincheng_definition.csv"
    rooms_csv = data_folder / "sparky_rooms_Jincheng_definition.csv"
    victims_csv = data_folder / "sparky_victims_Jincheng_definition.csv"

    portal_data = pd.read_csv(portals_csv)
    room_data = pd.read_csv(rooms_csv)
    victim_data = pd.read_csv(victims_csv)

    graph = MapParser.parse_map_data(portal_data, room_data, victim_data)


    # Get position
    pos, fix = graph.better_layout()
    pos = graph.flip_z(pos)
    pos = graph.clockwise90(pos)
    weight_labels = nx.get_edge_attributes(graph,'weight')

    plot_graph(graph, pos, weight_labels, save="JC")
    # # animate_graph(graph, pos, weight_labels)

    # plot_random_graph()

