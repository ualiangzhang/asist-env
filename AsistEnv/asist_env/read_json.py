import pandas as pd
import json
import re


def read_json_file(difficulty):
    with open("data/Falcon_map.json", 'r') as load_map_json:
        map_json = json.load(load_map_json)

    if difficulty == 'easy':
        file_name = "data/HSRData_TrialMessages_CondBtwn-NoTriageNoSignal_CondWin-FalconEasy-StaticMap_Trial-120_Team-na_Member-51_Vers-1.metadata"
    elif difficulty == 'medium':
        file_name = "data/HSRData_TrialMessages_CondBtwn-TriageSignal_CondWin-FalconMed-StaticMap_Trial-151_Team-na_Member-62_Vers-3.metadata"
    else:
        file_name = "data/HSRData_TrialMessages_CondBtwn-NoTriageNoSignal_CondWin-FalconHard-StaticMap_Trial-122_Team-na_Member-52_Vers-3.metadata"

    with open(file_name, 'r') as load_victim_json:
        for line in load_victim_json:
            data = json.loads(line)
            if data["topic"] == 'ground_truth/mission/victims_list':
                victim_json = data['data']
            elif data["topic"] == "ground_truth/semantic_map/updates":
                map_updates_json = data['data']['updates']

    portal_data = {'id': [], 'loc': [], 'connections': [], 'isOpen': []}
    room_data = {'id': [], 'name': [], 'loc': [], 'loc_tl': [], 'loc_br': [], 'connections': []}
    victim_data = {'id': [], 'loc': [], 'type': []}

    # update map info
    if 'additions' in map_updates_json.keys():
        for modi in map_updates_json['additions']['locations']:
            map_json['locations'].append(modi)

        for modi in map_updates_json['additions']['connections']:
            map_json['connections'].append(modi)

        for modi in map_updates_json['additions']['objects']:
            map_json['objects'].append(modi)

    if 'deletions' in map_updates_json.keys():
        for modi in map_updates_json['deletions']['connections']:
            for i in range(len(map_json['connections'])):
                if map_json['connections'][i]['id'] == modi:
                    map_json['connections'].remove(map_json['connections'][i])
                    break

    if 'modifications' in map_updates_json.keys():
        for modi in map_updates_json['modifications']['locations']:
            for i in range(len(map_json['locations'])):
                if map_json['locations'][i]['id'] == modi['id']:
                    if 'bounds' in modi.keys() and modi['bounds'] is not None:
                        map_json['locations'][i]['bounds'] = modi['bounds']
                    elif 'child_locations' in modi.keys() and modi['child_locations'] is not None:
                        map_json['locations'][i]['child_locations'] = modi['child_locations']
                    break

        for modi in map_updates_json['modifications']['connections']:
            for i in range(len(map_json['connections'])):
                if map_json['connections'][i]['id'] == modi['id']:
                    map_json['connections'][i]['connected_locations'] = modi['connected_locations']
                    break

    for key, value in map_json.items():
        if key == 'locations':
            for i in range(len(map_json[key])):
                if 'child_locations' not in map_json[key][i]:
                    room_id = map_json[key][i]['id']
                    if map_json[key][i]['name'].startswith('Part of'):
                        room_name = map_json[key][i]['name'][8:].strip()
                    else:
                        room_name = map_json[key][i]['name'].strip()
                    coordinate_x = map_json[key][i]['bounds']['coordinates'][0]['x']
                    coordinate_z = map_json[key][i]['bounds']['coordinates'][0]['z']
                    coordinate_x2 = map_json[key][i]['bounds']['coordinates'][1]['x']
                    coordinate_z2 = map_json[key][i]['bounds']['coordinates'][1]['z']
                    connection = []
                    room_data['id'].append(str(room_id))
                    room_data['name'].append(re.sub('[\\\']', '\'', room_name))
                    room_data['loc'].append(
                        str(((float(coordinate_x2) + float(coordinate_x)) // 2,
                             (float(coordinate_z2) + float(coordinate_z)) // 2)))
                    room_data['loc_tl'].append(str((coordinate_x, coordinate_z)))
                    room_data['loc_br'].append(str((coordinate_x2, coordinate_z2)))
                    room_data['connections'].append(connection)

        elif key == 'connections':
            door_id = 1
            for i in range(len(map_json[key])):
                door_id = map_json[key][i]['id']
                coordinate_x = map_json[key][i]['bounds']['coordinates'][0]['x']
                coordinate_z = map_json[key][i]['bounds']['coordinates'][0]['z']
                connection = []
                for conn in map_json[key][i]['connected_locations']:
                    connection.append(conn)
                # portal_data['id'].append('d' + str(door_id))
                # door_id += 1
                portal_data['id'].append(door_id)
                portal_data['loc'].append(str((coordinate_x, coordinate_z)))
                portal_data['connections'].append(str(connection))
                portal_data['isOpen'].append('True')

    victim_id = 0
    for vic in victim_json['mission_victim_list']:
        victim_id += 1
        victim_data['id'].append('v' + str(victim_id))
        victim_data['loc'].append(str((vic['x'], vic['z'])))
        if vic['block_type'] == 'block_victim_1':
            victim_data['type'].append('Green')
        else:
            victim_data['type'].append('Gold')

        room_idx = 0
        for room_name in room_data['name']:
            if vic['room_name'] == 'The Computer Farm':
                vic['room_name'] = 'Computer Farm'
            if vic['room_name'] == 'Open Break Area':
                vic['room_name'] = 'Break Room'
            if vic['room_name'] == room_name:
                vic_x = float(vic['x'])
                vic_z = float(vic['z'])
                idx = room_data['loc_tl'][room_idx].index(',')
                room_x = float(room_data['loc_tl'][room_idx][1:idx])
                room_z = float(room_data['loc_tl'][room_idx][idx + 1:-1])
                idx = room_data['loc_br'][room_idx].index(',')
                room_x2 = float(room_data['loc_br'][room_idx][1:idx])
                room_z2 = float(room_data['loc_br'][room_idx][idx + 1:-1])

                if room_x <= vic_x <= room_x2 and room_z <= vic_z <= room_z2:
                    room_data['connections'][room_idx].append('v' + str(victim_id))
                    break
            room_idx += 1

    for idx in range(len(room_data['connections'])):
        room_data['connections'][idx] = str(room_data['connections'][idx])

    room_data.pop('name')
    room_data.pop('loc_tl')
    room_data.pop('loc_br')

    return pd.DataFrame.from_dict(room_data), pd.DataFrame.from_dict(portal_data), pd.DataFrame.from_dict(victim_data)
