from .strategies_to_be_incorporated import best_next_move_for_strategy

STRATEGIES = ["convert", "attack", "flee"]
DEPTH = 3


def heuristic(humans, allies, enemies):
    """ simple heuristic here """
    result = sum([allies.values()]) - sum(enemies.values())
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
                                                                 and min_dist_en < min_dist_al):
            result += humans[human]
        elif min_dist_en is not None:
            result -= humans[human]
    for ally in allies:
        dmin = None
        enemy = None
        for en in enemies:
            d = max(abs(ally[0]-en[0]), abs(ally[1]-en[1]))
            if dmin is None or d < dmin:
                dmin = d
                enemy = en
        if dmin <= 2:
            if allies[ally] > 1.5*enemies[enemy]:
                result += enemies[enemy]
            elif 1.5*allies[ally] < enemies[enemy]:
                result -= allies[ally]
            else:
                p = allies[ally]/(2*enemies[enemy])
                result += (p**2)*allies[ally] - ((1-p)**2)*enemies[enemy]
    return result


def get_next_move_alpha_beta(depth, grid, ally):
    return alpha_beta_max(depth, grid.humans, grid.allies, grid.enemies, ally, None, True)


def alpha_beta_max(depth, humans, allies, enemies, ally, value, get_moves=False):
    if depth <= 0:
        return heuristic(humans, allies, enemies)
    else:
        interval = (None, value)
        children = get_relevant_children(humans, allies, enemies, ally)
        i = 0
        move = None
        while i < len(children) and (interval[0] is None or interval[1] is None or interval[0] < interval[1]):
            child = children[i]
            i += 1
            val = alpha_beta_min(depth-1, child[0], child[1], child[2], interval[0], ally)
            if get_moves and (interval[0] in None or val > interval[0]):
                move = child[3]
            interval = (val, interval[1])
        if get_moves:
            return move
        return interval[0]


def alpha_beta_min(depth, humans, allies, enemies, value, ally):
    if depth <= 0:
        return heuristic(humans, allies, enemies)
    else:
        interval = (value, None)
        children = get_relevant_children_enemies(humans, allies, enemies, ally)
        i = 0
        while i < len(children) and (interval[0] is None or interval[1] is None or interval[0] < interval[1]):
            child = children[i]
            i += 1
            val = alpha_beta_max(depth - 1, child[0], child[1], child[2], interval[1], ally)
            interval = (interval[0], val)
        return interval[1]


def get_relevant_children(humans, allies, enemies, ally):
    possible_moves = []
    for strategy in STRATEGIES:
        possible_moves.extend(best_next_move_for_strategy(strategy, ally, humans, allies, enemies))
    children = [(humans, dict(allies), enemies, None)]
    for move in possible_moves:
        new_allies = dict(allies)
        if new_allies[ally] == move[2]:
            del new_allies[ally]
            if (move[0], move[1]) not in new_allies:
                new_allies[(move[0], move[1])] = 0
            new_allies[(move[0], move[1])] += move[2]
        elif move[2] > 0:
            new_allies[ally] -= move[2]
            if (move[0], move[1]) not in new_allies:
                new_allies[(move[0], move[1])] = 0
            new_allies[(move[0], move[1])] += move[2]
        children.append((humans, new_allies, enemies, move))
    return children


def get_relevant_children_enemies(humans, allies, enemies, ally):
    children_wrong_order = get_relevant_children(humans, enemies, allies, ally)
    children = []
    for child in children_wrong_order:
        children.append((child[0], child[2], child[1], child[3]))
    return children


def get_dest_alpha_beta(grid, ally):
    return get_next_move_alpha_beta(DEPTH, grid, ally)
