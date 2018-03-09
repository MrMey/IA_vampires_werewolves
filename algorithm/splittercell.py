import logging
from operator import itemgetter
logging.basicConfig(level = logging.DEBUG)


from grid.grid import Grid



def get_distance(srce, dest):
    return max(abs(dest[0] - srce[0]), abs(dest[1] - srce[1]))


def get_closest_point(grid, srce, dest, avoid_enemies = True, avoid_stronger_humans = True):
    moves = Grid.get_closest_points(srce, dest)
    idx = 0
    iter_pos = True
    while iter_pos and idx < len(moves):
        # if all conditions are met then choose position else iterates
        iter_pos = False
        next_pos = (srce[0] + moves[idx][0], srce[1] + moves[idx][1])
        logging.debug('next_post {} vs ally {}'.format(next_pos, grid.allies[srce]))

        if next_pos not in grid.get_range(srce):
            logging.debug('destination not in range {}'.format(grid.get_range(srce)))
            iter_pos = True
        elif avoid_enemies and next_pos in grid.get_enemy_range():
            logging.debug('destination in enemy range')
            iter_pos = True
        elif avoid_stronger_humans and next_pos in grid.humans:
            if grid.humans[next_pos] >= grid.allies[srce]:
                logging.debug('destination in human range')
                iter_pos = True
        idx += 1
    return srce[0] + moves[idx-1][0], srce[1] + moves[idx-1][1]



def choose_allies(grid, ally):
    allies = sorted([ (get_distance(ally,al), al) for al in grid.allies ], key=itemgetter(0))
    return allies[1][1] # On prend le 2ème élément car le 1er est nous-mêmes.


def choose_humans(grid, ally):
    humans = sorted([ (get_distance(ally, hu), hu) for hu in grid.humans ], key=itemgetter(0))
    nb_al = grid.allies[ally]
    for i in range(len(grid.humans)):
        hu = humans[i][1]
        if grid.humans[hu] < nb_al:
            return hu
    return choose_allies(grid, ally)

def choose_enemies(grid, ally):
    enemies = sorted([ (get_distance(ally, en), en) for en in grid.enemies ], key=itemgetter(0))
    nb_al = grid.allies[ally]
    for i in range(len(grid.enemies)):
        en = enemies[i][1]
        if grid.enemies[en] < 1.5*nb_al:
            return en
    return choose_allies(grid, ally)

def choose_suicide(grid,ally):
    enemies = sorted([ (get_distance(ally, en), en) for en in grid.enemies ], key=itemgetter(0))
    enemy = enemies[0]
    if enemy[0] == 1:
        return enemy[1]
    elif enemy[0] > 2:
        return enemy[1]
    return None

def get_dest(grid, ally):
    # Si il y a des humains
    #   Si le plus proche est battable, l'attaquer
    #   Sinon, aller au 2ème plus proche, etc.
    #   Si aucun n'est battable, aller vers l'allié le plus proche pour merger
    # Sinon
    #   Si l'ennemi le plus proche est battable, l'attaquer
    #   Sinon, aller au 2ème plus proche, etc.
    #   Si aucun n'est battable, aller vers l'allié le plus proche pour merger
    move = []
    if grid.allies[ally] == 1:
        target = choose_suicide(grid,ally)
        if target:
            logging.debug("target : {}".format(target))
            dest = get_closest_point(grid,ally,target, avoid_enemies = False)
            grid.add_locked_cell(dest)
            move += [(ally[0], ally[1], grid.get_group_at(ally[0],ally[1]), dest[0], dest[1])]
    elif len(grid.humans) > 0:
        target = choose_humans(grid, ally)
        logging.debug("humans : {}".format(grid.humans))
        logging.debug("target : {}".format(target))
        dest = get_closest_point(grid, ally, target)
        grid.add_locked_cell(dest)
        extra = min(max(grid.allies[ally] - grid.get_group_at(target[0],target[1]) - 1, 0),1)
        logging.debug("extra units : {}".format(extra))
        move += [(ally[0], ally[1], grid.get_group_at(ally[0],ally[1]) - extra, dest[0], dest[1])]

    else:
        target = choose_enemies(grid, ally)
        dest = get_closest_point(grid, ally, target)
        grid.add_locked_cell(dest)
        move += [(ally[0], ally[1], grid.get_group_at(ally[0],ally[1]), dest[0], dest[1])]
    
    logging.debug('move {}'.format(move))

    
    return move