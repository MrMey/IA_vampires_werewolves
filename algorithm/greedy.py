from grid.grid import Grid
from operator import itemgetter


def get_distance(srce, dest):
    return max(abs(dest[0] - srce[0]), abs(dest[1] - srce[1]))

def get_closest_point(grid, srce, dest, avoid_enemies=False):
    if avoid_enemies:
        offsets = Grid.get_closest_points(srce, dest)
        idx = 0
        while (((srce[0] + offsets[idx][0], srce[1] + offsets[idx][1]) not in grid.get_range(srce)
               or (srce[0] + offsets[idx][0], srce[1] + offsets[idx][1]) in grid.get_enemy_range())
                and  idx < len(offsets)-1):
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

def get_dest(grid, ally):
    # Si il y a des humains
    #   Si le plus proche est battable, l'attaquer
    #   Sinon, aller au 2ème plus proche, etc.
    #   Si aucun n'est battable, aller vers l'allié le plus proche pour merger
    # Sinon
    #   Si l'ennemi le plus proche est battable, l'attaquer
    #   Sinon, aller au 2ème plus proche, etc.
    #   Si aucun n'est battable, aller vers l'allié le plus proche pour merger

    if len(grid.humans) > 0:
        target = choose_humans(grid, ally)
        dest = get_closest_point(grid, ally, target, True)
    else:
        target = choose_enemies(grid, ally)
        dest = get_closest_point(grid, ally, target, False)
    return dest