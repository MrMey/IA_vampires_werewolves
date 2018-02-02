import numpy as np
import copy

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
    def __init__(self, width, height):
        self._grid = np.empty((width, height), Group)
        for i in range(width):
            for j in range(height):
                self._grid[i, j] = Group(NON, 0)

    def _get_width(self):
        return self._grid.shape[0]

    def _get_height(self):
        return self._grid.shape[1]

    width = property(_get_width)
    height = property(_get_height)

    def update_group(self, x, y, nb_hum, nb_vam, nb_wol):
        if nb_hum == nb_vam == nb_wol == 0:
            self._grid[x, y].species = NON
            self._grid[x, y].number = 0
        elif nb_hum > 0:
            self._grid[x, y].species = HUM
            self._grid[x, y].number = nb_hum
        elif nb_vam > 1:
            self._grid[x, y].species = VAM
            self._grid[x, y].number = nb_vam
        else:
            self._grid[x, y].species = WOL
            self._grid[x, y].number = nb_wol

    def get_group_at(self, x, y):
        return self._grid[x, y]

    def get_number_of(self, species):
        count = 0
        for i in range(self._grid.shape[0]):
            for j in range(self._grid.shape[1]):
                group = self._grid[i, j]
                if group.species == species:
                    count += group.number
        return count

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
