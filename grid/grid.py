import numpy as np

NON = 0
HUM = 1
VAM = 2
WOL = 3

class Grid:
    def __init__(self, height, width):
        self._height = height
        self._width = width
        self.allies = []
        self.humans = []
        self.ennemies = []

    def _get_width(self):
        return self._width

    def _get_height(self):
        return self._height

    width = property(_get_width)
    height = property(_get_height)

    def update_all_groups(self,content):
        n = content[0]
        if n != 0:
            liste = content[1]
            for i in range(0, n):
                position = [ x for x in liste[i*5:i*5+5] ]
                print(position)
                self.update_group(*position)

    def update_group(self, x, y, nb_hum, nb_vam, nb_wol):
        if nb_hum == nb_vam == nb_wol == 0:
            if (x,y) in self.allies:
                self.allies.pop((x,y))
            elif (x,y) in self.humans:
                self.humans.pop((x,y))
            elif (x,y) in self.ennemies:
                self.ennemies.pop((x,y))

        elif nb_hum > 0:
            self.humans[(x,y)] = nb_hum
            if (x,y) in self.allies:
                self.allies.pop((x,y))
            elif (x,y) in self.ennemies:
                self.ennemies.pop((x,y))

        elif nb_vam > 0:
            self.allies[(x,y)] = nb_vam
            if (x,y) in self.humans:
                self.humans.pop((x,y))
            elif (x,y) in self.ennemies:
                self.ennemies.pop((x,y))

        elif nb_wol > 0:
            self.ennemies[(x,y)] = nb_wol
            if (x,y) in self.humans:
                self.humans.pop((x,y))
            elif (x,y) in self.allies:
                self.allies.pop((x,y))

    def get_group_at(self, x, y):
        """Return the number of members in a cell"""
        if (x,y) in self.humans:
            return self.humans[(x,y)]
        elif (x,y) in self.allies:
            return self.allies[(x,y)]
        elif (x,y) in self.ennemies:
            return self.ennemies[(x,y)]

    def get_number_of(self, species):
        count = 0
        if species == HUM:
            for hu in self.humans:
                count += self.humans[hu]
        elif species == VAM:
            for ally in self.allies:
                count += self.allies[ally]
        elif species == WOL:
            for ennemy in self.ennemies:
                count += self.ennemies[ennemy]
        return count

    def get_distance(self, srce, dest):
        return abs(dest[0]-srce[0])+abs(dest[1]-srce[1])

    def is_reachable(self,srce,dest):
        if [abs(srce[0] - dest[0]),abs(srce[1]-dest[1])] in [[1,1],[1,0],[0,1],[1,1],[0,0]]:
            return True
        else:
            return False
    
    @staticmethod
    def get_closest_points(srce, dest):
        moves = []
        if srce[0] < dest[0]:
            if srce[1] < dest[1]:
                moves = [[1, 1], [0, 1], [1, 0]] + moves
            elif srce[1] > dest[1]:
                moves = [[1, -1], [0, -1], [1, 0]] + moves
            else:
                moves = [[1, 0], [1, -1], [1, 1]] + moves
        elif srce[0] > dest[0]:
            if srce[1] < dest[1]:
                moves = [[- 1, 1], [0, 1], [- 1, 0]] + moves
            elif srce[1] > dest[1]:
                moves = [[- 1, - 1], [0, - 1], [- 1, 0]] + moves
            else:
                moves = [[- 1, 0], [-1, -1], [-1, 1]] + moves
        else:
            if srce[1] < dest[1]:
                moves = [[0, 1], [-1, 1], [1, 1]] + moves
            elif srce[1] > dest[1]:
                moves = [[0, - 1], [- 1, - 1], [1, -1]] + moves

        return moves

    def get_range(self, pos):
        offsets = [[1, 1], [1, 0], [1, -1], [0, -1],[-1, -1], [-1, 0], [-1, 1], [0, 1],[0,0]]
        cells = []
        for idx in range(len(offsets)):
            x = pos[0] + offsets[idx][0]
            y = pos[1] + offsets[idx][1]
            if 0 <= x < self.height and 0 <= y < self.width:
                cells += [[x, y]]
        return cells

    def get_ennemy_range(self):
        cells = []
        for ennemy in self.ennemies:
            cells += ennemy
        return cells

    """def compute_heuristic_simple(self, humans, allies, ennemies):
        fitness = 0
        for group in allies:
            fitness += group.get_group_at(group[0], group[1]).number
        return fitness"""
