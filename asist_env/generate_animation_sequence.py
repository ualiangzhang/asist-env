import pandas as pd
from pathlib import Path
from environment import MapParser
import graph
from datetime import datetime


def time_str_to_timestamp(str):
    datetime_object = datetime.strptime(str, "%Y-%m-%dT%H:%M:%S.%fZ")
    return int(datetime_object.timestamp())

data_folder = Path("data")

portals_csv = data_folder / "sparky_portals.csv"
rooms_csv = data_folder / "sparky_rooms.csv"
victims_csv = data_folder / "sparky_victims.csv"

portal_data = pd.read_csv(portals_csv)
room_data = pd.read_csv(rooms_csv)
victim_data = pd.read_csv(victims_csv)

g = MapParser.parse_map_data(portal_data, room_data, victim_data)


pd.set_option("display.max_rows", None, "display.max_columns", None)

data_folder = Path("data")
processed_csv = data_folder / "processed_07.csv"

raw_sequence = pd.read_csv(processed_csv)
state_sequence = pd.DataFrame(columns=['time', 'state', 'score'])

last_state = None

start_time = time_str_to_timestamp(raw_sequence["@timestamp"][0])
cumulative_score = 0
for index, row in raw_sequence.iterrows():
    if row["Room_in"] != "None":
        if row["triage_result"] == "SUCCESSFUL":
            curr_state = "v" + row["event_triage_victim_id"]

        else:
            curr_state = row["Room_in"]
    # elif row["Portal_in"] != "None":
    #     curr_state = row["Portal_in"]
    else:
        continue

    curr_time = time_str_to_timestamp(row["@timestamp"])

    if curr_state != last_state:
        if last_state is not None and g[curr_state].type == graph.NodeType.Room and \
                g[last_state].type == graph.NodeType.Room:
            for n in g.get_neighbors(g[curr_state]):
                if n.type == graph.NodeType.Portal:
                    linked = n.linked_portal
                    if g[last_state].id == linked.get_connected_room_id():
                        state_sequence = state_sequence.append({
                            'time': curr_time - start_time - 1,
                            'state': linked.id,
                            'score': cumulative_score
                        }, ignore_index=True)
                        # print(linked.id, curr_state, last_state)
                        # input()
                        state_sequence = state_sequence.append({
                            'time': curr_time - start_time - 1,
                            'state': n.id,
                            'score': cumulative_score
                        }, ignore_index=True)
                        # print(n.id, curr_state, last_state)
                        # input()

        if g[curr_state].type == graph.NodeType.Victim:
            if g[curr_state].victim_type == graph.VictimType.Green:
                cumulative_score += 10
            if g[curr_state].victim_type == graph.VictimType.Yellow:
                cumulative_score += 30

        last_state = curr_state


        state_sequence = state_sequence.append({
            'time': curr_time - start_time,
            'state': curr_state,
            'score': cumulative_score
        }, ignore_index=True)
        # print(curr_state, curr_state, last_state)
        # input()

print(state_sequence)
state_sequence.to_csv(data_folder / "animation_sequence_processed_07.csv", index=False)
