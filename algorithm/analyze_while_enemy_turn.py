from threading import Thread
from algorithm.alphabeta import *


def analyze_while_enemy_playing(grid):
    for child in get_all_children_no_split(grid.humans, grid.allies, grid.enemies, (grid.width, grid.height), True):
        Thread(target=alpha_beta_max, args=(DEPTH, child[0], child[1], child[2], (None, None), (grid.width, grid.height), False)).start()

