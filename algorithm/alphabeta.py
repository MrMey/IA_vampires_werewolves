from .strategies_to_be_incorporated import best_next_move_for_strategy

STRATEGIES = ["convert", "attack", "flee"]


def heuristic(humans, allies, enemies):
    """ dummy heuristic """
    return 0


def get_next_move_alpha_beta(depth, humans, allies, enemies):
    return alpha_beta_max(depth, humans, allies, enemies, None)


def alpha_beta_max(depth, humans, allies, enemies, value):
    if depth <= 0:
        return heuristic(humans, allies, enemies)
    else:
        interval = (None, value)
        children = get_relevant_children(humans, allies, enemies)
        i = 0
        while i < len(children) and (interval[0] is None or interval[1] is None or interval[0] < interval[1]):
            child = children[i]
            i += 1
            val = alpha_beta_min(depth-1, child[0], child[1], child[2], interval[0])
            interval = (val, interval[1])
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
            val = alpha_beta_max(depth - 1, child[0], child[1], child[2], interval[1])
            interval = (interval[0], val)
        return interval[1]


def get_relevant_children(humans, allies, enemies):
    possible_moves = {}
    for group in allies:
        if group not in possible_moves:
            possible_moves[group] = []
        for strategy in STRATEGIES:
            possible_moves[group].append(best_next_move_for_strategy(strategy, group, humans, allies, enemies))
    for group in possible_moves:
        possible_moves[group].append(group)
    children = []
    which_moves = len(possible_moves)*[0]
    corr = {}
    i = 0
    for group in possible_moves:
        corr[i] = group
        i += 1
    while still_new_moves(which_moves, possible_moves, corr):
        moves = [(possible_moves[corr[i]], possible_moves[corr[i]][which_moves[i]]) for i in range(len(possible_moves))]
        new_allies = dict(allies)
        for move in moves:
            temp = new_allies[move[0]]
            new_allies.pop(move[0])
            new_allies[move[1]] = temp
        children.append((humans, new_allies, enemies))
        to_next_moves(which_moves, possible_moves, corr)
    return children


def get_relevant_children_enemies(humans, allies, enemies):
    children_wrong_order = get_relevant_children(humans, enemies, allies)
    children = []
    for child in children_wrong_order:
        children.append((child[0], child[2], child[1]))
    return children


def still_new_moves(which_moves, possible_moves, corr):
    for i in range(len(possible_moves)):
        if which_moves[i] < len(possible_moves[corr[i]]):
            return True
    return False


def to_next_moves(which_moves, possible_moves, corr):
    for k in reversed(range(len(which_moves))):
        if which_moves[k] < len(possible_moves[corr[k]]) - 1:
            which_moves[k] += 1
            break
        else:
            which_moves[k] = 0
