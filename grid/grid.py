
class Grid:
    def __init__(self, height, width):
        self._height = height
        self._width = width
        self.vampires = {}
        self.humans = {}
        self.wolves = {}
        self.locked_cell = []

    def set_species(self,species):
        if species not in ['wolves','vampires']:
            raise ValueError('species must be wolves or vampires')
        self.species = species

    def _get_allies(self):
        if self.species == "wolves":
            return self.wolves
        else:
            return self.vampires
    allies = property(_get_allies)

    def _get_enemies(self):
        if self.species == "wolves":
            return self.vampires
        else:
            return self.wolves

    enemies = property(_get_enemies)

    def _get_width(self):
        return self._width

    def _get_height(self):
        return self._height

    width = property(_get_width)
    height = property(_get_height)

    def delete_key(self, dico, key):
        try:
            del dico[key]
        except KeyError:
            pass

    def get_key(self, dico, key):
        try:
            return dico[key]
        except KeyError:
            return 0

    def update_group(self, x, y, nb_hum, nb_vam, nb_wol):
        if nb_hum == nb_vam == nb_wol == 0:
            self.delete_key(self.vampires, (x,y))
            self.delete_key(self.humans, (x,y))
            self.delete_key(self.wolves, (x,y))

        elif nb_hum > 0:
            self.humans[(x,y)] = nb_hum
            self.delete_key(self.vampires, (x,y))
            self.delete_key(self.wolves, (x,y))

        elif nb_vam > 0:
            self.vampires[(x,y)] = nb_vam
            self.delete_key(self.humans, (x,y))
            self.delete_key(self.wolves, (x,y))

        elif nb_wol > 0:
            self.wolves[(x, y)] = nb_wol
            self.delete_key(self.humans, (x,y))
            self.delete_key(self.vampires, (x,y))

    def update_all_groups(self,content):
        n = content[0]
        if n != 0:
            liste = content[1]
            for i in range(0, n):
                position = [ x for x in liste[i*5:i*5+5] ]
                print(position)
                self.update_group(*position)

    def update_map(self,content):
        self.clean_locked_cell()
        self.update_all_groups(content)

    def initiate_all_groups(self, content, ally_start):
        n = content[0]
        if n != 0:
            liste = content[1]
            for i in range(0, n):
                position = [x for x in liste[i * 5:i * 5 + 5]]
                if (position[0], position[1]) == ally_start:
                    if position[3] != 0:
                        self.set_species('vampires')
                    elif position[4] != 0:
                        self.set_species('wolves')
                    else:
                        raise Exception("did not find our species")

                print(position)
                self.update_group(*position)

    def get_group_at(self, x, y):
        """Return the number of members in a cell"""
        hum = self.get_key(self.humans, (x,y))
        vam = self.get_key(self.vampires, (x,y))
        wol = self.get_key(self.wolves, (x,y))
        return max(hum, vam, wol)

    def get_number_of(self, species):
        if species == 'HUM':
            return sum(self.humans.values())
        elif species == 'VAM':
            return sum(self.vampires.values())
        elif species == 'WOL':
            return sum(self.wolves.values())

    def get_distance(self, srce, dest):
        return abs(dest[0]-srce[0]) + abs(dest[1]-srce[1])

    @staticmethod
    def get_closest_points(srce, dest):
        moves = []
        if srce[0] < dest[0]:
            if srce[1] < dest[1]:
                moves = [(1,1), (0,1), (1,0)] + moves
            elif srce[1] > dest[1]:
                moves = [(1,-1), (0,-1), (1,0)] + moves
            else:
                moves = [(1,0), (1,-1), (1,1)] + moves
        elif srce[0] > dest[0]:
            if srce[1] < dest[1]:
                moves = [(-1,1), (0,1), (-1,0)] + moves
            elif srce[1] > dest[1]:
                moves = [(-1,-1), (0,-1), (-1,0)] + moves
            else:
                moves = [(-1,0), (-1,-1), (-1,1)] + moves
        else:
            if srce[1] < dest[1]:
                moves = [(0,1), (-1,1), (1,1)] + moves
            elif srce[1] > dest[1]:
                moves = [(0,-1), (-1,-1), (1,-1)] + moves

        return moves

    def get_range(self, pos):
        offsets = ((1,1), (1,0), (1,-1), (0,-1), (-1,-1), (-1,0), (-1,1), (0,1), (0,0))
        cells = []
        for idx in range(len(offsets)):
            x = pos[0] + offsets[idx][0]
            y = pos[1] + offsets[idx][1]
            if self.is_in_map((x,y)) and not self.is_locked_cell((x,y)):
                cells += [(x, y)]
        return cells

    def is_in_map(self, pos):
        return 0 <= pos[1] < self.height and 0 <= pos[0] < self.width

    def is_locked_cell(self,pos):
        return pos in self.locked_cell

    def add_locked_cell(self,pos):
        self.locked_cell += [pos]

    def clean_locked_cell(self):
        self.locked_cell = []

    def get_enemy_range(self):
        cells = []
        for enemy in self.enemies:
            cells += self.get_range(enemy)
        return cells

