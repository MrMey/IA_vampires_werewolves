import numpy as np

NON = 0
HUM = 1
VAM = 2
WOL = 3


class Group:
    def __init__(self, species, number):
        self._species = species
        self._number = number

    def _get_number(self):
        return self._number

    def _set_number(self, number):
        self._number = number

    def _get_species(self):
        return self._species

    def _set_species(self, species):
        self._species = species

    number = property(_get_number, _set_number)
    species = property(_get_species, _set_species)


class Grid:
    def __init__(self, height, width):
        self._grid = np.empty((height, width), Group)
        for i in range(height):
            for j in range(width):
                self._grid[i, j] = Group(NON, 0)
        self.allies = []
        self.humans = []
        self.ennemies = []

    def _get_width(self):
        return self._grid.shape[1]

    def _get_height(self):
        return self._grid.shape[0]

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
            self._grid[y, x].species = NON
            self._grid[y, x].number = 0
            if [y,x] in self.allies:
                self.allies.remove([y, x])
            if [y,x] in self.humans:
                self.humans.remove([y, x])
            if [y,x] in self.ennemies:
                self.ennemies.remove([y, x])
        elif nb_hum > 0:
            self._grid[y, x].species = HUM
            self._grid[y, x].number = nb_hum
            if [y,x] not in self.humans:
                self.humans.append([y, x])
            if [y,x] in self.allies:
                self.allies.remove([y, x])
            if [y,x] in self.ennemies:
                self.ennemies.remove([y, x])
        elif nb_vam > 0:
            self._grid[y, x].species = VAM
            self._grid[y, x].number = nb_vam
            if [y,x] not in self.allies:
                self.allies.append([y, x])
            if [y,x] in self.humans:
                self.humans.remove([y, x])
            if [y,x] in self.ennemies:
                self.ennemies.remove([y, x])
        else:
            self._grid[y, x].species = WOL
            self._grid[y, x].number = nb_wol
            if [y,x] not in self.ennemies:
                self.ennemies.append([y, x])
            if [y,x] in self.humans:
                self.humans.remove([y, x])
            if [y,x] in self.allies:
                self.ennemies.remove([y, x])

    def get_group_at(self, x, y):
        return self._grid[y, x]

    def get_number_of(self, species):
        count = 0
        for i in range(self._grid.shape[0]):
            for j in range(self._grid.shape[1]):
                group = self._grid[i, j]
                if group.species == species:
                    count += group.number
        return count

    def get_distance(self, srce, dest):
        return abs(dest[0]-srce[0])+abs(dest[1]-srce[1])

    def is_reachable(self,srce,dest):
        if [abs(srce[0] - dest[0]),abs(srce[1]-dest[1])] in [[1,1],[1,0],[0,1],[1,1],[0,0]]:
            return True
        else:
            return False

    def get_closest_points(self, srce, dest):
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
            cells += self.get_range(ennemy)
        return cells

    def get_closest_point(self, srce, dest, avoid_ennemies = False):
        if avoid_ennemies:
            offsets = self.get_closest_points(srce,dest)
            idx = 0
            while ([srce[0] + offsets[idx][0], srce[1] + offsets[idx][1]] not in self.get_range(srce) or [srce[0] + offsets[idx][0], srce[1] + offsets[idx][1]] in self.get_ennemy_range()) and  idx < len(offsets)-1:
                idx += 1
            return srce[0] + offsets[idx][0], srce[1] + offsets[idx][1]
        else:
            if srce[0] < dest[0]:
                return srce[0] + 1, srce[1]
            elif srce[0] > dest[0]:
                return srce[0] - 1, srce[1]
            elif srce[1] < dest[1]:
                return srce[0], srce[1] + 1
            else:
                return srce[0], srce[1] - 1

    def compute_heuristic_simple(self, humans, allies, ennemies):
        fitness = 0
        for group in allies:
            fitness += group.get_group_at(group[0], group[1]).number
        return fitness

    """def get_grid_with_move(self, xstart, ystart, xend, yend, number):
        if self._grid[xstart, ystart] is None or abs(xend - xstart) > 1 or abs(ystart - yend) > 1 or \
                number > self._grid[xstart, ystart].number:
            raise ValueError("Invalid move")
        current_grid_copy = copy.deepcopy(self)
        if self._grid[xend, yend] is not None and self._grid[xend, yend].species != self._grid[xstart, ystart].species:
            factor = 2
            species = self._grid[xstart, ystart].species
            if species != HUM:
                factor += 1
            if 2*number//factor >= self._grid[xend, yend]:
                if species == HUM:
                    current_grid_copy._grid[xstart, ystart].number -= number
                    if current_grid_copy._grid[xstart, ystart].number == 0:
                        current_grid_copy._grid[xstart, ystart] = None
                    current_grid_copy._grid[xend, yend].species = species
                    current_grid_copy._grid[xend, yend].number += number
                else:
                    current_grid_copy._grid[xstart, ystart].number -= number
                    if current_grid_copy._grid[xstart, ystart].number == 0:
                        current_grid_copy._grid[xstart, ystart] = None
                    current_grid_copy._grid[xend, yend].species = species
                    current_grid_copy._grid[xend, yend].number = number
            elif 2*self._grid[xend, yend]//factor >= number and self._grid[xend, yend].species != HUM:
                current_grid_copy._grid[xstart, ystart].number -= number
                if current_grid_copy._grid[xstart, ystart].number == 0:
                    current_grid_copy._grid[xstart, ystart] = None
            else:
                raise Exception("Battle")
        current_grid_copy = copy.deepcopy(self)
        current_grid_copy._grid[xstart, ystart].number -= number
        species = current_grid_copy._grid[xstart, ystart].species
        if current_grid_copy._grid[xstart, ystart].number == 0:
            current_grid_copy._grid[xstart, ystart] = None
        if current_grid_copy._grid[xend, yend] is None:
            current_grid_copy._grid[xend, yend] = Group(species, number)
        else:
            current_grid_copy._grid[xend, yend].number += number"""
