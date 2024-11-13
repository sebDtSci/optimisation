import sys
import math

class Case:
    def __init__(self, index: int, cell_type: int, resources: int, neighbors: list[int], my_ants: int, opp_ants: int):
        self.index = index
        self.cell_type = cell_type
        self.resources = resources
        self.neighbors = neighbors
        self.my_ants = my_ants
        self.opp_ants = opp_ants

cases :list[Case] = []
# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

number_of_cells = int(input())  # amount of hexagonal cells in this map
for i in range(number_of_cells):
    # _type: 0 for empty, 1 for eggs, 2 for crystal
    # initial_resources: the initial amount of eggs/crystals on this cell
    # neigh_0: the index of the neighbouring cell for each direction
    _type, initial_resources, neigh_0, neigh_1, neigh_2, neigh_3, neigh_4, neigh_5 = [int(j) for j in input().split()]
    case: Case = Case(
        index = i,
        cell_type = _type,
        resources = initial_resources,
        neighbors = list(filter(lambda id: id > -1,[neigh_0, neigh_1, neigh_2, neigh_3, neigh_4, neigh_5])),
        my_ants = 0,
        opp_ants = 0
        )
    cases.append(case)

number_of_bases = int(input())
bases:list = []
for i in input().split():
    my_base_index = int(i)
    bases.append(my_base_index)
for i in input().split():
    opp_base_index = int(i)

# game loop
while True:
    for i in range(number_of_cells):
        # resources: the current amount of eggs/crystals on this cell
        # my_ants: the amount of your ants on this cell
        # opp_ants: the amount of opponent ants on this cell
        resources, my_ants, opp_ants = [int(j) for j in input().split()]

        cases[i].resources = resources
        cases[i].my_ants = my_ants
        cases[i].opp_ants = opp_ants
    
    cmd:list = []
    for case in cases:
        if case.resources > 1:
            cmd.append(f'LINE {bases[0]} {case.index} 1')
            # break


    print(';'.join(cmd))
    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr, flush=True)
    


    # WAIT | LINE <sourceIdx> <targetIdx> <strength> | BEACON <cellIdx> <strength> | MESSAGE <text>
