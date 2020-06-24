## TODO

1. Model the Sparky map layout

2. Both rooms and doors/portals should be represented as nodes.
    - rooms are "volumes" or "zones"
    - portals are also zones
    - all room nodes are connected by portal nodes

3. Implement a coordinate system
    - Use the coordinates to define the corners of each room.
    - include location variables to describe agent's current position, victim locations, portal locations
    - use coordinates to represent distance between nodes

4. Implement a time component
    - how long it takes for agent to move from one position to another (within one room or between rooms)
    - how long to triage victims
    - time will possibly be an input to the reward functions.

5. Define rewards
    - constants at the beginning of script
    - reward functions
