import pandas as pd
import json
import re


def read_json_file():
    with open("data/Saturn_1.0_sm_v1.0.json", 'r') as load_map_json:
        map_json = json.load(load_map_json)

    portal_data = {'id': [], 'loc': [], 'connections': [], 'isOpen': []}
    room_data = {'id': [], 'name': [], 'loc': [], 'loc_tl': [], 'loc_br': [], 'connections': []}

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

    for idx in range(len(room_data['connections'])):
        room_data['connections'][idx] = str(room_data['connections'][idx])

    room_data.pop('name')
    room_data.pop('loc_tl')
    room_data.pop('loc_br')

    file_name = "saturn_room.json"
    with open(file_name, "w") as outfile:
        json.dump(room_data, outfile, ensure_ascii=False, indent=4)

    file_name = "saturn_portal.json"
    with open(file_name, "w") as outfile:
        json.dump(portal_data, outfile, ensure_ascii=False, indent=4)


    return pd.DataFrame.from_dict(room_data), pd.DataFrame.from_dict(portal_data)


read_json_file()
