import itertools
import time

# from algorithm.strategies_to_be_incorporated import best_next_move_for_strategy

STRATEGIES = ["convert", "attack", "flee"]
DEPTH = 5


def heuristic(humans, allies, enemies, probabilistic):
    if len(allies) == 0:
        return -2*(sum(enemies.values()) - sum(humans.values()))
    if len(enemies) == 0:
        return 2 * (sum(enemies.values()) - sum(humans.values()))
    toph = time.time()
    result = 2*(sum(allies.values()) - sum(enemies.values()))
    # print(result)
    if not probabilistic:
        for human in humans:
            min_dist_al = None
            for ally in allies:
                d = max(abs(ally[0] - human[0]), abs(ally[1] - human[1]))
                if (min_dist_al is None or d < min_dist_al) and allies[ally] > humans[human]:
                    min_dist_al = d
            min_dist_en = None
            for enemy in enemies:
                d = max(abs(enemy[0] - human[0]), abs(enemy[1] - human[1]))
                if min_dist_en is None or d < min_dist_en and enemies[enemy] > humans[human]:
                    min_dist_en = d
            if (min_dist_en is None and min_dist_al is not None) or (min_dist_en is not None and min_dist_al is not None
                                                                     and min_dist_al < min_dist_en):
                result += humans[human] / (max(1, min_dist_al))
                # print(result)
            elif min_dist_en is not None:
                result -= humans[human] / (max(1, min_dist_en))
                # print(result)
        for ally in allies:
            dmin = None
            enemy = None
            for en in enemies:
                d = max(abs(ally[0] - en[0]), abs(ally[1] - en[1]))
                if dmin is None or d < dmin:
                    dmin = d
                    enemy = en
            if dmin is not None:
                if allies[ally] > 1.5 * enemies[enemy]:
                    result += enemies[enemy] / (max(1, dmin))
                    # print(result)
                elif 1.5 * allies[ally] < enemies[enemy]:
                    result -= allies[ally] / (max(1, dmin))
                    # print(result)
                else:
                    p = allies[ally] / (2 * enemies[enemy])
                    result += (p**2) * allies[ally] / (max(1, dmin)) - ((1 - p)**2) * enemies[enemy] / (max(1, dmin))
                    # print(result)
    else:
        result -= max(enemies.values())
    # print("{} {} {} {} heuristic: {}\n".format(humans, allies, enemies, probabilistic, result))
    return result


def get_next_move_alpha_beta(depth, grid):
    return alpha_beta_max(depth, grid.humans, grid.allies, grid.enemies, (None, None), (grid.width, grid.height), True)


def alpha_beta_max(depth, humans, allies, enemies, interval, dimensions, get_moves=False):
    # print("MAX {}".format(depth))
    h = heuristic(humans, allies, enemies, False)
    if depth <= 0:
        return h
    else:
        inter = interval
        children = get_relevant_children(humans, allies, enemies, dimensions)
        if len(children) == 0:
            return h
        i = 0
        move = None
        while i < len(children) and (inter[0] is None or inter[1] is None
                                     or inter[0] < inter[1]):
            child = children[i]
            i += 1
            if child[4]:
                heu = heuristic(child[0], child[1], child[2], True)
                val = heu
            else:
                val = alpha_beta_min(depth - 1, child[0], child[1], child[2], inter, dimensions)
            if inter[0] is None or (val is not None and val > inter[0]):
                move = child[3]
                inter = (val, inter[1])
            # print(inter)
            """if depth == 6:
                print(child, intervals)"""
        if get_moves:
            # print("FINAL MOVE: {}\n".format(move))
            return move
        return inter[0]


def alpha_beta_min(depth, humans, allies, enemies, interval, dimensions):
    # print("MIN {}".format(depth))
    h = heuristic(humans, allies, enemies, False)
    if depth <= 0:
        return h
    else:
        inter = interval
        children = get_relevant_children_enemies(humans, allies, enemies, dimensions)
        if len(children) == 0:
            return h
        i = 0
        move = None
        while i < len(children) and (inter[0] is None or inter[1] is None
                                     or inter[0] < inter[1]):
            child = children[i]
            i += 1
            if child[4]:
                heu = heuristic(child[0], child[1], child[2], True)
                val = heu
            else:
                val = alpha_beta_max(depth - 1, child[0], child[1], child[2], inter, dimensions)
            improved = False
            if inter[1] is None or (val is not None and val < inter[1]):
                move = child[3]
                inter = (inter[0], val)
            # print(inter)
        # print("FINAL MOVE: {}\n".format(move))
        return inter[1]


"""def get_relevant_children(humans, allies, enemies):
    moves = {ally: [] for ally in allies}
    for ally in moves:
        for strategy in STRATEGIES:
            moves[ally].extend(best_next_move_for_strategy(strategy, ally, humans, allies, enemies))
    return get_children_from_moves(humans, allies, enemies, moves)"""


def get_relevant_children(humans, allies, enemies, dimensions):
    # print("dimensions: {}".format(dimensions))
    moves = {ally: [(ally[0] + i, ally[1] + j, allies[ally]) for i in range(-1, 2) for j in range(-1, 2)
                    if 0 <= ally[0] + i < dimensions[0] and 0 <= ally[1] + j < dimensions[1]] for ally in allies}
    return get_children_from_moves(humans, allies, enemies, moves)


def get_children_from_moves(humans, allies, enemies, moves):
    # print(moves)
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
    # print("BEGIN")
    for moves_set in p:
        if is_actual_move(moves_set, corr):
            new_humans, new_allies, new_enemies, probabilistic = dict(humans), dict(allies), dict(enemies), False
            for i in range(len(moves_set)):
                temp = get_child_from_move(new_humans, new_allies, new_enemies, corr[i], (moves_set[i][0],
                                                                                          moves_set[i][1]),
                                           moves_set[i][2])
                new_humans, new_allies, new_enemies, probabilistic = temp[0], temp[1], temp[2], probabilistic or temp[3]
            children.append(
                (new_humans, new_allies, new_enemies, {corr[i]: moves_set[i] for i in range(len(moves_set))},
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
        else:
            if number == t:
                p = 0.5
            elif number < t:
                p = number/(2*t)
            else:
                p = (number / t) - 0.5
            new_allies[destination] = (p ** 2) * number
            new_enemies[destination] = ((1 - p) ** 2) * t
            probabilistic = True
    else:
        new_allies[destination] = number
    return new_humans, new_allies, new_enemies, probabilistic


def is_actual_move(moves_set, corr):
    for i in range(len(corr)):
        if corr[i] != (moves_set[i][0], moves_set[i][1]):
            return True
    return False


def get_relevant_children_enemies(humans, allies, enemies, dimensions):
    children_wrong_order = get_relevant_children(humans, enemies, allies, dimensions)
    children = []
    for child in children_wrong_order:
        children.append((child[0], child[2], child[1], child[3], child[4]))
    return children


def get_dest_alpha_beta(grid):
    return get_next_move_alpha_beta(DEPTH, grid)


"""humans = {(1, 1): 1, (3, 2): 1}
allies = {(2, 2): 3}
enemies = {(5, 5): 3}

print("origin heuristic: {}".format(heuristic(humans, allies, enemies, False, None)))
top = time.time()
print(alpha_beta_max(2, humans, allies, enemies, (None, None), (15, 15), None, True))
print(time.time()-top)
print(total_time_heuristic)"""
