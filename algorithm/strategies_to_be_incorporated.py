# -*- coding: utf-8 -*-

"""humans = {(1, 1): 6, (2, 5): 2, (5, 2): 1}
allies = {(2, 3): 3, (5, 5): 3, (2, 1): 1}
enemies = {(2, 4): 12, (3, 2): 1}
group = (2, 3)"""
import logging
import math
import random
# quelques remarques générales:

# 1. Les fusion possibles sont "prise en compte" c'est à dire que pour fuire un groupe un peu plus grand que nous
# on peut tenter de fusioner avec un groupe proche suffisament grand. Néanmoins, l'autre groupe ne doit pas bouger
# pour cela, ce qui n'est pas prévu par ce code car les groupes sont traités ici indépendemment

# 2. Comme les groupes sont traités indépendemment, deux groupes riquent d'attaquer le même groupe d'humain ou d'enemis

# 3. Il n'y a pour le moment pas séparation de groupe de faite, ça peut être une quatrième stratégie à implémenter

# 5. Attention il peut y avoir des doublons en fonction des stratégies

# 6. les contours de la carte (x_max et y_max sont encore sur la carte)
# et les cases interdites (cases qui contenait un groupe juste avant)


def best_next_move_for_strategy(strategy, group, humans, allies, enemies, locked_cells, x_max, y_max, nbr_cibles=3):
    # getting the imediate context of the group
    # just_around, i, j = get_imediate_context(group, humans, enemies, allies)
    i = group[0]
    j = group[1]
    # best move depending of the strategy
    moves = []
    if strategy == "convert":
        target = find_closest(group, humans, 1, nbr_cibles, allies)
        locked = locked_extend("convert", locked_cells, humans, enemies, allies[group])
        # on suppose qu'un groupe allié sur le chemin ne pose pas de problème:
        #     soit il fusionne soit il est dans locked_cells
        # si l'enemi est faible, on le "mange" au passage
        # si l'enemi est moyen
        #               -> on l'évite
        # si l'enemi est fort
        #               -> on abandonne d'aller convertir la maison dans cette direction
        #                  car un déplacement vers elle nous ferait tuer le groupe
        for t in target:
            # trouve la direction à prendre...
            i_new, j_new = find_direction_for_target(group, t)
            #print('     target : ' + str(t) + '  direction : ' + str((i_new, j_new)))
            # vérifie qu'il n'y a pas d'obstacles et que ce n'est pas hors de la carte
            if (i_new,j_new) in locked or hors_carte(i_new, j_new, x_max, y_max):
                (i1, j1, i2, j2) = try_avoiding(i, j, i_new, j_new)
                if (i1, j1) not in locked and not hors_carte(i1, j1, x_max, y_max) and (i1, j1) not in moves:
                    moves.append(((i1, j1, allies[group], strategy),))
                if (i2, j2) not in locked and not hors_carte(i2, j2, x_max, y_max) and (i2, j2) not in moves:
                    moves.append(((i2, j2, allies[group], strategy),))
            elif ((i_new, j_new, allies[group], strategy),) not in moves and ((i_new, j_new) not in locked):
                moves.append(((i_new, j_new, allies[group], strategy),))
    elif strategy == "attack":
        # on attaque aussi les groupes pas 1,5 fois plus faibles que nous
        target = find_closest(group, enemies, 0.33, nbr_cibles, allies)
        locked = locked_extend("attack", locked_cells, humans, enemies, allies[group])
        # print(locked)
        for t in target:
            # trouve la direction à prendre...
            i_new, j_new = find_direction_for_target(group, t)
            #print('     target : ' + str(t) + '  direction : ' + str((i_new, j_new)))
            # vérifie qu'il n'y a pas d'obstacles et que ce n'est pas hors de la carte
            if (i_new,j_new) in locked or hors_carte(i_new, j_new, x_max, y_max):
                (i1, j1, i2, j2) = try_avoiding(i, j, i_new, j_new)
                if (i1, j1) not in locked and not hors_carte(i1, j1, x_max, y_max) and (i1, j1) not in moves:
                    moves.append(((i1, j1, allies[group], strategy),))
                if (i2, j2) not in locked and not hors_carte(i2, j2, x_max, y_max) and (i2, j2) not in moves:
                    moves.append(((i2, j2, allies[group], strategy),))
            elif (i_new, j_new) not in moves and (i_new, j_new) not in locked:
                moves.append(((i_new, j_new, allies[group], strategy),))
    elif strategy == "flee":
        locked = locked_extend("flee", locked_cells, humans, enemies, allies[group])
        for i_new in range(i-1, i+2):
            for j_new in range(j-1, j+2):
                if (i_new, j_new) not in locked and not hors_carte(i_new, j_new, x_max, y_max):
                    moves.append(((i_new, j_new, allies[group], strategy),))
    elif strategy == "split":
        locked = locked_extend("flee", locked_cells, humans, enemies, allies[group])
        targets = find_targets_split(group, humans, allies, enemies)
        moves_for_group = []
        nb = allies[group]
        for k in range(len(targets[0])):
            if k == len(targets[0])-1 and len(targets[1])==0:
                to_move = nb
            else:
                to_move = humans[targets[0][k]]+1
            i_new, j_new = find_direction_for_target(group, targets[0][k])
            if (i_new,j_new) in locked or hors_carte(i_new, j_new, x_max, y_max):
                (i1, j1, i2, j2) = try_avoiding(i, j, i_new, j_new)
                if (i1, j1) not in locked and not hors_carte(i1, j1, x_max, y_max) and (i1, j1) not in moves_for_group:
                    moves_for_group.append((i1, j1, to_move, strategy))
                    nb -= to_move
                elif (i2, j2) not in locked and not hors_carte(i2, j2, x_max, y_max) and (i2, j2) not in moves_for_group:
                    moves_for_group.append((i2, j2, to_move, strategy))
                    nb -= to_move
            elif (i_new, j_new) not in moves_for_group and (i_new, j_new) not in locked:
                moves_for_group.append((i_new, j_new, to_move, strategy))
                nb -= to_move
        for p in range(len(targets[1])):
            if p == len(targets[1])-1:
                to_move = nb
            else:
                to_move = math.ceil(enemies[targets[1][p]])
            i_new, j_new = find_direction_for_target(group, targets[1][p])
            if (i_new,j_new) in locked or hors_carte(i_new, j_new, x_max, y_max):
                (i1, j1, i2, j2) = try_avoiding(i, j, i_new, j_new)
                if (i1, j1) not in locked and not hors_carte(i1, j1, x_max, y_max) and (i1, j1) not in moves_for_group:
                    moves_for_group.append((i1, j1, to_move, strategy))
                    nb -= to_move
                elif (i2, j2) not in locked and not hors_carte(i2, j2, x_max, y_max) and (i2, j2) not in moves_for_group:
                    moves_for_group.append((i2, j2, to_move, strategy))
                    nb -= to_move
            elif (i_new, j_new) not in moves_for_group and (i_new, j_new) not in locked:
                moves_for_group.append((i_new, j_new, to_move, strategy))
                nb -= to_move
        moves.append(tuple(moves_for_group))
    elif strategy == "final_rounds":
        locked = locked_extend("flee", locked_cells, humans, enemies, allies[group])
        # if several groups, lets merge
        if len(allies)>1:
            first=0
            for a in allies:
                if first==0:
                    if group != a:
                        first = a
            x, y = find_direction_for_target(group, first)
            (i1, j1, i2, j2) = try_avoiding(i, j, x, y)
            # logging.debug("LAST ROUND BIS: {} {}".format(group, (x,y)))
            if (x, y) not in locked and hors_carte(x,y, x_max, y_max):
                # logging.debug("LAST ROUND")
                moves.append(((x, y, allies[group], strategy),))
            if (i1, j1) not in locked and hors_carte(i1,j1, x_max, y_max):
                # logging.debug("LAST ROUND")
                moves.append(((i1, j1, allies[group], strategy),))
            if (i2, j2) not in locked and hors_carte(i2,j2, x_max, y_max):
                # logging.debug("LAST ROUND")
                moves.append(((i2, j2, allies[group], strategy),))

        # if our group is weaker
        for e,n in enemies.items():
            if n > 1.5 * allies[group]:
                # to avoid but we already lost... :(
                # no more problem of locked_cells since we are alone ...
                x, y = find_direction_for_target(group, e)
                (i1, j1, i2, j2) = try_avoiding(i, j, x, y)
                for i_new in range(i-1, i+2):
                    for j_new in range(j-1, j+2):
                        if (i_new != i or j_new != j) and not hors_carte(i_new, j_new, x_max, y_max):
                            if (i_new, j_new) != (i1, j1) and (i_new, j_new) != (i2, j2) and (i_new, j_new) != (x, y):
                                if (i_new, j_new) not in locked:
                                    # logging.debug("LAST ROUND")
                                    moves.append(((i_new, j_new, allies[group], strategy),))
            else:
                x, y = find_direction_for_target(group, e)
                #logging.debug("LAST ROUND BIS: {} {}".format(group, (x,y)))
                if (x,y) not in locked:
                    # logging.debug("LAST ROUND")
                    moves.append(((x, y, allies[group], strategy),))
    elif strategy == "random":
        i_new = i + random.randint(-1, 1)
        if i_new != i:
            j_new = j + random.randint(-1, 1)
        else:
            j_new = j + [-1, 1][random.randint(0, 1)]
        if i_new < 0:
            i_new += 1
        if i_new > x_max:
            i_new -= 1
        if j_new < 0:
            j_new += 1
        if j_new > y_max:
            j_new -= 1
        moves.append(((i_new, j_new, allies[group]),))
    else:
        raise Exception("unknown strategy, please implement it")
    return moves


def find_direction_for_target(group, t):
    i_new = group[0]
    j_new = group[1]
    if t[0] > group[0]:
        i_new = group[0] + 1
    elif t[0] < group[0]:
        i_new = group[0] - 1
    if t[1] > group[1]:
        j_new = group[1] + 1
    elif t[1] < group[1]:
        j_new = group[1] - 1
    return i_new, j_new


# def get_convertible_humans_in_imediate_context(just_around, humans, allies, group):
#     """
#     humains convertissable dans les cases juste autour
#     """
#     best = []
#     for h in range(len(just_around["humans"])):
#         if humans[just_around["humans"][h]] < allies[group]:
#             best.append((just_around["humans"][h], humans[just_around["humans"][h]]))
#     return best


# def get_imediate_context(group, humans, enemies, allies):
#     """
#     Donne la position du groupe et pour les cases autour, divisé entre les humains, les alliés et les enemis
#     """
#     just_around = {"humans": [], "enemies": [], "allies": []}
#     i = group[0]
#     j = group[1]
#     for h in humans:
#         if (h[0] == i - 1 or h[0] == i or h[0] == i + 1) and (h[1] == j - 1 or h[1] == j or h[1] == j + 1):
#             just_around["humans"].append(h)
#     for e in enemies:
#         if (e[0] == i - 1 or e[0] == i or e[0] == i + 1) and (e[1] == j - 1 or e[1] == j or e[1] == j + 1):
#             just_around["enemies"].append(e)
#     for a in allies:
#         if (a[0] == i - 1 or a[0] == i or a[0] == i + 1) and (a[1] == j - 1 or a[1] == j or a[1] == j + 1):
#             if a != group:
#                 just_around["allies"].append(a)
#     return just_around, i, j


def find_closest(group, category, rate, max_return, allies):
    """
    renvoie la liste des max_return plus proches cases correspondant à des groupes de catégory, en
    évitant les confrontations qui ne mènent pas à la victoire de façon certaine"""
    if len(category) == 0:
        return []
    best_choice = []
    for loc, nb in category.items():
        distance = max(loc[0] - group[0], loc[1] - group[1])
        if rate * nb <= allies[group]:  # bataille que l'on peut gagner
            best_choice.append(loc)
            if len(best_choice) > max_return:
                m = len(best_choice)
                for i in range(len(best_choice)):
                    if max(best_choice[i][0] - group[0], best_choice[i][1] - group[1]) > distance:
                        distance = max(best_choice[i][0] - group[0], best_choice[i][1] - group[1])
                        m = i
                if m < len(best_choice):
                    best_choice.pop(m)
    return best_choice


def find_targets_split(group, humans, allies, enemies):
    nb = allies[group]
    human_targets, enemies_targets = [], []
    for human in humans:
        if nb <= 1:  # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            break
        if humans[human] <= nb:
            human_targets.append(human)
            nb -= humans[human] + 1
    if nb > 1:
        for enemy in enemies:
            if nb <= 1: # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                break
            if nb > 1.5*enemies[enemy]+1:
                enemies_targets.append(enemy)
                nb -= 1.5*enemies[enemy]+1
    return human_targets, enemies_targets


def try_avoiding(i, j, i_new, j_new):
    """
    le pion est sur la case (i,j) et doit se déplacer sur la case (i_new,j_new), mais cette case n'est pas accessible.
    On renvoie alors les deux cases qui permettent d'éviter l'ostacle tout en allant à peu près dans la bonne direction
    """
    if i == i_new:
        return i+1, j_new, i-1, j_new
    elif j == j_new:
        return i_new, j+1, i_new, j-1
    return i, j_new, i_new, j


def locked_extend(strategy, locked_cells, humans, enemies, group_nbr):
    """
    Renvoie les cases à éviter absolument
    :param strategy:
    :param locked_cells: cases de départ de groupes allies
    :param humans:
    :param enemies:
    :param group_nbr: nombre d'éléments dans le groupe considéré
    :return: l'ensemble des cases à éviter : les cases de départ des autres alliés,
                les cases d'humains trop nombreux convertis, les cases des enemis trop forts pour être attaqués
                (pas pour la strategie attack) et les cases autour s'il est même assez puissant pour nous attaquer
    """
    locked_list = locked_cells
    if strategy == "convert":
        for human, nbr in humans.items():
            if nbr > group_nbr:
                locked_list.append(human)
        for enemie, nbr in enemies.items():
            if nbr > group_nbr * 1.5 :
                locked_list += [enemie,
                                (enemie[0]-1, enemie[1]-1),
                                (enemie[0], enemie[1]-1),
                                (enemie[0]-1, enemie[1]),
                                (enemie[0]+1, enemie[1]-1),
                                (enemie[0]+1, enemie[1]),
                                (enemie[0]+1, enemie[1]+1),
                                (enemie[0]-1, enemie[1]+1),
                                (enemie[0], enemie[1]+1)]
            elif nbr * 1.5 >= group_nbr :
                locked_list += [enemie]
    elif strategy == "attack":
        for human, nbr in humans.items():
            if nbr > group_nbr:
                locked_list.append(human)
        for enemie, nbr in enemies.items():
            if nbr > group_nbr * 1.5 :
                locked_list += [enemie,
                                (enemie[0]-1, enemie[1]-1),
                                (enemie[0], enemie[1]-1),
                                (enemie[0]-1, enemie[1]),
                                (enemie[0]+1, enemie[1]-1),
                                (enemie[0]+1, enemie[1]),
                                (enemie[0]+1, enemie[1]+1),
                                (enemie[0]-1, enemie[1]+1),
                                (enemie[0], enemie[1]+1)]
    elif strategy == "flee":
        for human, nbr in humans.items():
            if nbr > group_nbr:
                locked_list.append(human)
        for enemie, nbr in enemies.items():
            if nbr * 1.5 >= group_nbr :
                locked_list += [enemie,
                                (enemie[0]-1, enemie[1]-1),
                                (enemie[0], enemie[1]-1),
                                (enemie[0]-1, enemie[1]),
                                (enemie[0]+1, enemie[1]-1),
                                (enemie[0]+1, enemie[1]),
                                (enemie[0]+1, enemie[1]+1),
                                (enemie[0]-1, enemie[1]+1),
                                (enemie[0], enemie[1]+1)]
    return locked_list


def hors_carte(i, j, x, y):
    """ renvoie False si (i,j) est bien dans la carte"""
    return i < 0 or j < 0 or i > x or j > y


if __name__ == "__main__":
    humans = {(1, 1): 6, (2, 5): 2, (5, 2): 1}
    allies = {(2, 3): 12, (5, 5): 3, (2, 1): 1}
    enemies = {(3, 2): 1, (2, 4): 12}
    group = (2, 3)
    locked_cells = []
    x_max = 20
    y_max = 20
    a = best_next_move_for_strategy("flee", group, humans, allies, enemies, locked_cells, x_max, y_max, nbr_cibles=3)
    print(a)