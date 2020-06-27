from environment import MapParser
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import networkx as nx

plt.figure(figsize=(15,15))

data_folder = Path("data")

portals_csv = data_folder / "sparky_portals.csv"
rooms_csv = data_folder / "sparky_rooms.csv"
victims_csv = data_folder / "sparky_victims.csv"

portal_data = pd.read_csv(portals_csv)
room_data = pd.read_csv(rooms_csv)
victim_data = pd.read_csv(victims_csv)

graph = MapParser.parse_map_data(portal_data, room_data, victim_data)
# pos = nx.spring_layout(graph)
# print(type(pos))
# print(pos[graph.nodes_list[0]])
# print(type(pos[graph.nodes_list[0]]))
pos, fix = graph.better_layout()
pos = graph.flip_z(pos)
pos = graph.clockwise90(pos)

color_map = graph.better_color()
weight_labels = nx.get_edge_attributes(graph,'weight')
# pos = nx.spring_layout(graph, k=0.9, iterations=3, pos=pos, fixed=fix, weight=3)

nx.draw(graph, pos, node_color=color_map, with_labels=True)
nx.draw_networkx_edge_labels(graph, pos, edge_labels=weight_labels)

plt.show()