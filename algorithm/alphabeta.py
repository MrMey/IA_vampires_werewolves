import itertools
import time
from .strategies_to_be_incorporated import best_next_move_for_strategy

STRATEGIES = ["convert", "attack", "flee"]
DEPTH = 3


total_time_heuristic = 0


def heuristic(humans, allies, enemies):
    """ simple heuristic here """
    global total_time_heuristic
    toph = time.time()
    result = sum(allies.values()) - sum(enemies.values())
    for human in humans:
        min_dist_al = None
        for ally in allies:
            d = max(abs(ally[0]-human[0]), abs(ally[1]-human[1]))
            if (min_dist_al is None or d < min_dist_al) and allies[ally] > humans[human]:
                min_dist_al = d
        min_dist_en = None
        for enemy in enemies:
            d = max(abs(enemy[0] - human[0]), abs(enemy[1] - human[1]))
            if min_dist_en is None or d < min_dist_en and enemies[enemy] > humans[human]:
                min_dist_en = d
        if (min_dist_en is None and min_dist_al is not None) or (min_dist_en is not None and min_dist_al is not None
                                                                 and min_dist_al < min_dist_en):
            result += humans[human]/2
        elif min_dist_en is not None:
            result -= humans[human]/2
    for ally in allies:
        dmin = None
        enemy = None
        for en in enemies:
            d = max(abs(ally[0]-en[0]), abs(ally[1]-en[1]))
            if dmin is None or d < dmin:
                dmin = d
                enemy = en
        if dmin is not None and dmin <= 2:
            if allies[ally] > 1.5*enemies[enemy]:
                result += enemies[enemy]/2
            elif 1.5*allies[ally] < enemies[enemy]:
                result -= allies[ally]/2
            else:
                p = allies[ally]/(2*enemies[enemy])
                result += (p**2)*allies[ally]/2 - ((1-p)**2)*enemies[enemy]/2
    # print(humans, allies, enemies, result)
    total_time_heuristic += time.time() - toph
    return result


def get_next_move_alpha_beta(depth, grid):
    return alpha_beta_max(depth, grid.humans, grid.allies, grid.enemies, None, True)


def alpha_beta_max(depth, humans, allies, enemies, value, get_moves=False):
    if depth <= 0:
        return heuristic(humans, allies, enemies)
    else:
        interval = (None, value)
        children = get_relevant_children(humans, allies, enemies)
        i = 0
        move = None
        while i < len(children) and (interval[0] is None or interval[1] is None or interval[0] < interval[1]):
            child = children[i]
            i += 1
            if child[4]:
                val = heuristic(child[0], child[1], child[2])
            else:
                val = alpha_beta_min(depth-1, child[0], child[1], child[2], interval[0])
            if get_moves and (interval[0] is None or val > interval[0]):
                move = child[3]
            interval = (val, interval[1])
        if get_moves:
            return move
        return interval[0]


def alpha_beta_min(depth, humans, allies, enemies, value):
    if depth <= 0:
        return heuristic(humans, allies, enemies)
    else:
        interval = (value, None)
        children = get_relevant_children_enemies(humans, allies, enemies)
        i = 0
        while i < len(children) and (interval[0] is None or interval[1] is None or interval[0] < interval[1]):
            child = children[i]
            i += 1
            if child[4]:
                val = heuristic(child[0], child[1], child[2])
            else:
                val = alpha_beta_max(depth - 1, child[0], child[1], child[2], interval[1])
            interval = (interval[0], val)
        return interval[1]


"""def get_relevant_children(humans, allies, enemies):
    moves = {ally: [] for ally in allies}
    for ally in moves:
        for strategy in STRATEGIES:
            moves[ally].extend(best_next_move_for_strategy(strategy, ally, humans, allies, enemies))
    return get_children_from_moves(humans, allies, enemies, moves)"""


def get_relevant_children(humans, allies, enemies):
    moves = {ally: [(ally[0]+i, ally[1]+j, allies[ally]) for i in range(-1, 2) for j in range(-1, 2)] for ally in allies}
    return get_children_from_moves(humans, allies, enemies, moves)


def get_children_from_moves(humans, allies, enemies, moves):
    children = []
    i = 0
    corr = {}
    moves_for_allies = []
    for ally in moves:
        corr[i] = ally
        i += 1
        moves_for_allies.append(moves[ally])
    moves_for_allies = tuple(moves_for_allies)
    p = set(itertools.product(*moves_for_allies))
    for moves_set in p:
        new_humans, new_allies, new_enemies, probabilistic = dict(humans), dict(allies), dict(enemies), False
        for i in range(len(moves_set)):
            temp = get_child_from_move(new_humans, new_allies, new_enemies, corr[i], (moves_set[i][0], moves_set[i][1]),
                                       moves_set[i][2])
            new_humans, new_allies, new_enemies, probabilistic = temp[0], temp[1], temp[2], probabilistic or temp[3]
        children.append((new_humans, new_allies, new_enemies, {corr[i]: moves_set[i] for i in range(len(moves_set))},
                         probabilistic))
    return children


def get_child_from_move(new_humans, new_allies, new_enemies, origin, destination, number):
    probabilistic = False
    if number == new_allies[origin]:
        del new_allies[origin]
    else:
        new_allies[origin] -= number
    if destination in new_humans:
        t = new_humans[destination]
        if number > new_humans[destination]:
            del new_humans[destination]
            new_allies[destination] = number + t
        else:
            p = number / (2 * t)
            new_allies[destination] = (p ** 2) * (number + t)
            new_humans[destination] = ((1 - p) ** 2) * t
            probabilistic = True
    elif destination in new_allies:
        new_allies[destination] += number
    elif destination in new_enemies:
        t = new_enemies[destination]
        if number > 1.5 * t:
            del new_enemies[destination]
            new_allies[destination] = number
        elif t > number * 1.5:
            pass
        else:
            p = (number / t) - 0.5
            new_allies[destination] = (p ** 2)*(number)
            new_enemies[destination] = ((1 - p) ** 2) * t
            probabilistic = True
    else:
        new_allies[destination] = number
    return new_humans, new_allies, new_enemies, probabilistic


def get_relevant_children_enemies(humans, allies, enemies):
    children_wrong_order = get_relevant_children(humans, enemies, allies)
    children = []
    for child in children_wrong_order:
        children.append((child[0], child[2], child[1], child[3], child[4]))
    return children


def get_dest_alpha_beta(grid):
    return get_next_move_alpha_beta(DEPTH, grid)


humans = {(1, 1): 1, (3, 2): 1}
allies = {(2, 6): 3, (3, 3): 3}
enemies = {(2, 4): 3, (5, 5): 3}

print("origin heuristic: {}".format(heuristic(humans, allies, enemies)))
top = time.time()
print(alpha_beta_max(DEPTH, humans, allies, enemies, None, True))
print(time.time()-top)
print(total_time_heuristic)
