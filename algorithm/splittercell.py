# -*- coding: utf-8 -*-

import logging
from operator import itemgetter
logging.basicConfig(level = logging.DEBUG)

from threading import Lock, Thread

from grid.grid import Grid



def get_distance(srce, dest):
    return max(abs(dest[0] - srce[0]), abs(dest[1] - srce[1]))


def get_closest_point(grid, srce, dest, avoid_enemies = True, avoid_stronger_humans = True, avoid_allies = False):
    moves = grid.get_closest_points(srce, dest)
    idx = 0
    iter_pos = True
    logging.debug("possible moves : {}".format(moves))
    while iter_pos and idx < len(moves):
        # if all conditions are met then choose position else iterates
        iter_pos = False
        next_pos = moves[idx]
        if avoid_enemies and next_pos in grid.get_enemy_range():
            logging.debug('destination in enemy range')
            iter_pos = True
        elif avoid_stronger_humans and next_pos in grid.humans:
            if grid.humans[next_pos] > grid.allies[srce]:
                logging.debug('destination in human range')
                iter_pos = True
        idx += 1
    return moves[idx-1][0], moves[idx-1][1]

def choose_humans(grid, ally, nb_ally = None):
    if not nb_ally:
        nb_ally = grid.allies[ally]
    
    moves = []
    humans = sorted([ (get_distance(ally, hu), hu) for hu in grid.humans if grid.humans[hu] <=  nb_ally],
    key=itemgetter(0))

    logging.debug("ally : {}, nb_ally : {}, weaker humans {}".format(ally,nb_ally,humans))

    if len(humans) > 0:
        iter = 0
        while nb_ally > 0 and iter < min(3,len(humans)):
            target = humans[iter][1]
            if grid.humans[target] <= nb_ally:
                dest = get_closest_point(grid, ally, target)
                moves += [(ally[0],ally[1], grid.humans[target], dest[0], dest[1])]
                logging.debug("moves {} toward {}".format((ally[0],ally[1],
                                grid.humans[target], dest[0], dest[1]),target))
                nb_ally -= grid.humans[target]
            iter += 1
        if nb_ally > 0:
            moves += [(moves[-1][0],moves[-1][1],nb_ally,moves[-1][3],moves[-1][4])]
            nb_ally = 0
    else:
        # s'il reste des allies on se regroupe
        if len(grid.allies) > 1:
            target = sorted([ (get_distance(ally,al), al) for al in grid.allies ], key=itemgetter(0))
            dest = target[1][1]
            moves += [(ally[0],ally[1], nb_ally, dest[0], dest[1])]
        # sinon on cherche un ennemies
        else:
            return choose_enemies(grid,ally,nb_ally)
    return moves

def choose_enemies(grid, ally, nb_ally = None):
    if not nb_ally:
        nb_ally = grid.allies[ally]
    moves = []
    enemies = sorted([ (get_distance(ally, en), en) for en in grid.enemies ], key=itemgetter(0))

    for i in range(len(grid.enemies)):
        en = enemies[i][1]
        if grid.enemies[en] < 1.5*nb_ally:

            dest = get_closest_point(grid, ally, en)
            moves += [(ally[0],ally[1], nb_ally, dest[0], dest[1])]
            return moves
    # s'il reste des allies on se regroupe
    if len(grid.allies) > 1:
            target = sorted([ (get_distance(ally,al), al) for al in grid.allies ], key=itemgetter(0))
            logging.debug("target {}".format(target))
            dest = get_closest_point(grid, ally, target[1][1])
            moves += [(ally[0],ally[1], nb_ally, dest[0], dest[1])]
            return moves
    # sinon on fuit
    return run_away(grid,ally)

def choose_screening(grid,ally, nb_ally = None):
    if not nb_ally:
        nb_ally = grid.allies[ally]
    moves = []
    enemies = sorted([ (get_distance(ally, en), en) for en in grid.enemies ], key=itemgetter(0))
    enemy = enemies[0]
    if enemy[0] == 1:
        dest = enemy[1]
        moves += [(ally[0],ally[1], nb_ally, dest[0], dest[1])]
        
    elif enemy[0] > 2:
        target = enemy[1]
        dest = get_closest_point(grid, ally, target, avoid_enemies = False)
        moves += [(ally[0],ally[1], nb_ally, dest[0], dest[1])]
    logging.debug("screening {}".format(moves))
    return moves

def run_away(grid,ally, nb_ally= None):
    if not nb_ally:
        nb_ally = grid.allies[ally]
    moves = grid.get_range(ally)
    dest = [move for move in moves if move not in grid.get_enemy_range()][0]
    return [(ally[0],ally[1], nb_ally, dest[0], dest[1])]

def spread(grid,ally,nb_cells, nb_ally = None):
    if not nb_ally:
        nb_ally = grid.allies[ally]
    enemies = sorted([ (get_distance(ally, en), en) for en in grid.enemies ], key=itemgetter(0))
    if enemies[0][0] <= 2 and grid.allies[ally] > 1:
        return run_away(grid,ally)

    next_pos = grid.get_range(ally)
    cases = min(nb_cells,nb_ally)
    moves = []

    child = 0
    while child < cases and child < len(next_pos):
        
        if next_pos[child] in grid.get_enemy_range():
            child +=1
        else:   
            moves += [(ally[0], ally[1], int(nb_ally/cases), next_pos[child][0], next_pos[child][1])]
            child +=1


    return moves
  
        
def get_dest(grid, ally):
    # Si il y a des humains
    #   Si le plus proche est battable, l'attaquer
    #   Sinon, aller au 2Ã¨me plus proche, etc.
    #   Si aucun n'est battable, aller vers l'alliÃ© le plus proche pour merger
    # Sinon
    #   Si l'ennemi le plus proche est battable, l'attaquer
    #   Sinon, aller au 2Ã¨me plus proche, etc.
    #   Si aucun n'est battable, aller vers l'alliÃ© le plus proche pour merger
    moves = []
    if grid.allies[ally] == 1:
        moves += choose_screening(grid,ally)
    else:
        moves += spread(grid,ally, 8)
    return moves

class SplittercellThread(Thread):
    def __init__(self, grid):
        Thread.__init__(self)
        self.grid = grid
        self.queue = []
    
    def run(self):
        for ally in self.grid.allies:
            logging.debug("humans: {}".format(self.grid.humans))
            logging.debug("allies: {}".format(self.grid.allies))
            logging.debug("enemies: {}".format(self.grid.enemies))

            move = get_dest(self.grid, ally)

            # move must be a list
            self.queue += move
