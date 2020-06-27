from environment import MapParser
import matplotlib.pyplot as plt
import matplotlib.animation
import pandas as pd
from pathlib import Path
import networkx as nx
matplotlib.use("TkAgg")

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


def animate_graph(graph, pos, weight_labels):
    # Animation update function
    def update(num):
        print(num)
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

    portals_csv = data_folder / "sparky_portals.csv"
    rooms_csv = data_folder / "sparky_rooms.csv"
    victims_csv = data_folder / "sparky_victims.csv"

    portal_data = pd.read_csv(portals_csv)
    room_data = pd.read_csv(rooms_csv)
    victim_data = pd.read_csv(victims_csv)

    graph = MapParser.parse_map_data(portal_data, room_data, victim_data)


    # Get position
    pos, fix = graph.better_layout()
    pos = graph.flip_z(pos)
    pos = graph.clockwise90(pos)
    weight_labels = nx.get_edge_attributes(graph,'weight')

    plot_graph(graph, pos, weight_labels, save="test")


