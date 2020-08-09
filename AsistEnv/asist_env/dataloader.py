"""
Prepare Minecraft map data for drawing a Graph.
Outputs:
    1) data/sparky_rooms.csv   : cols = 'id', 'loc', 'connections' (victim connections)
    2) data/sparky_portals.csv : cols = 'id', 'loc', 'connections', 'isOpen' (room connections)
    3) data/sparky_victims.csv : cols = 'id', 'loc', 'type'

"""
import pandas as pd

def get_midpoint(x0, z0, x1, z1):
    return ((x0+x1)/2, (z0+z1)/2)

# TODO: make command line interface, split up into functions.
sparky_rooms   = pd.read_csv('./data/ASIST_SparkyMap_Rooms_v5.5.csv')
sparky_portals = pd.read_csv('./data/ASIST_SparkyMap_Portals_v5.5.csv')
sparky_victims = pd.read_csv('./data/ASIST_SparkyMap_Victims_v5.5.csv')
sparky_portals['Index'] = sparky_portals['Index'].apply(lambda x: "p" + str(x))
sparky_victims['Index'] = sparky_victims['Index'].apply(lambda y: "v" + str(y))

# Make room data
df_sr = pd.DataFrame(columns=['id', 'loc', 'connections'])
for i in sparky_rooms.index:
    midpt = get_midpoint(sparky_rooms['x0'][i],sparky_rooms['z0'][i],sparky_rooms['x1'][i],sparky_rooms['z1'][i])
    df_sr = df_sr.append(
        {'id': sparky_rooms['RoomID'][i], 
         'loc': midpt, 
         'connections': []
         }, ignore_index=True)
    # add victim connections to the room
    for j in sparky_victims.index:
        if(sparky_victims['Victim Location'][j] == df_sr['id'][i]):
            df_sr['connections'][i].append(sparky_victims['Index'][j])

df_sr.to_csv('./data/sparky_rooms.csv', index=False)

# Make portal data
df_sp = pd.DataFrame(columns=['id', 'loc', 'connections', 'isOpen'])
for i in sparky_portals.index:
    midpt = get_midpoint(sparky_portals['x0'][i],sparky_portals['z0'][i],sparky_portals['x1'][i],sparky_portals['z1'][i])
    df_sp = df_sp.append(
        {'id': sparky_portals['Index'][i], 
         'loc': midpt, 
         'connections': [], 
         'isOpen': sparky_portals['visibility'][i]
         }, ignore_index=True)
    # add room connections to the portal
    for j in sparky_rooms.index:
        if(sparky_rooms['RoomID'][j] in {sparky_portals['Room0'][i], sparky_portals['Room1'][i]}):
            df_sp['connections'][i].append(sparky_rooms['RoomID'][j])

df_sp.to_csv('./data/sparky_portals.csv', index=False)

# Make victim data
df_sv = pd.DataFrame(columns=['id', 'loc', 'type'])
for i in sparky_victims.index:
    df_sv = df_sv.append(
        {'id':   sparky_victims['Index'][i], 
         'loc': (sparky_victims['X'][i], sparky_victims['Z'][i]),
         'type': sparky_victims['Color'][i]
        }, ignore_index=True)

df_sv.to_csv('./data/sparky_victims.csv', index=False)