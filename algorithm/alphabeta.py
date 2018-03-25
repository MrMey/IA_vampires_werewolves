# -*- coding: utf-8 -*-

import itertools
import time
import math
import logging
from threading import Lock, Thread

from algorithm.strategies_to_be_incorporated import best_next_move_for_strategy

STRATEGIES = ["simple", "split"]
DEPTH = 7

cache = {}


def cache_hash(humans, allies, enemies, depth, is_max_turn):
    """
    Computes the hash code of a given situation
    :param humans: the humans dictionary
    :param allies: the allies dictionary
    :param enemies: the enemies dictionary
    :param depth: the exploration depth (int)
    :param is_max_turn: boolean that's True iff it's the turn of max
    :return: the hash code
    """
    return hash((hash(frozenset(humans.items())), hash(frozenset(allies.items())), hash(frozenset(enemies.items())),
                 depth, is_max_turn))


def heuristic(humans, allies, enemies, probabilistic, x_max, y_max):
    """
    Computes the heuristic of a given situation
    :param humans: the humans dictionary
    :param allies: the allies dictionary
    :param enemies: the enemies dictionary
    :param probabilistic: boolean that tells if the situation is probabilistic
    :param x_max: the x dimension of the grid
    :param y_max: the y dimension of the grid
    :return: the associated heuristic
    """
    if len(allies) == 0 or (probabilistic and len(humans) != 0):  # avoids random battles while there are still humans
        return -2 * (sum(enemies.values()) + sum(humans.values()))
    if len(enemies) == 0:
        return 2 * (sum(allies.values()) + sum(humans.values()))
    result = 2 * (sum(allies.values()) - sum(enemies.values()))  # difference between number of allies and enemies
    for human in humans:  # takes into account the closest strong enough allies or enemies group from each human group
        min_dist_al = None
        for ally in allies:
            d = max(abs(ally[0] - human[0]), abs(ally[1] - human[1]))
            if (min_dist_al is None or d < min_dist_al) and allies[ally] >= humans[human]:
                min_dist_al = d
        min_dist_en = None
        for enemy in enemies:
            d = max(abs(enemy[0] - human[0]), abs(enemy[1] - human[1]))
            if min_dist_en is None or d < min_dist_en and enemies[enemy] >= humans[human]:
                min_dist_en = d
        if (min_dist_en is None and min_dist_al is not None) or (min_dist_en is not None and min_dist_al is not None
                                                                 and min_dist_al < min_dist_en):
            result += humans[human] / (max(1, min_dist_al))
        elif min_dist_en is not None:
            result -= humans[human] / (max(1, min_dist_en))
    for ally in allies:  # takes into account the closest ennemies group from each allies group
        dmin = None
        enemy = None
        for en in enemies:
            d = max(abs(ally[0] - en[0]), abs(ally[1] - en[1]))
            if dmin is None or d < dmin:
                dmin = d
                enemy = en
        if dmin is not None:
            if allies[ally] > 1.5 * enemies[enemy]:
                result += 0
            elif 1.5 * allies[ally] < enemies[enemy]:
                result -= allies[ally] / (max(1, dmin))
            else:
                p = allies[ally] / (2 * enemies[enemy])
                if len(humans) == 0:
                    result += min(0, ((p ** 2) * allies[ally] / (max(1, dmin))) - (
                            ((1 - p) ** 2) * enemies[enemy] / (max(1, dmin))))
                else:
                    result += (1 / len(humans)) * min(0, ((p ** 2) * allies[ally] / (max(1, dmin))) - (
                            ((1 - p) ** 2) * enemies[enemy] / (max(1, dmin))))

        result -= 0.001 * (abs(ally[0] - (x_max / 2)) / x_max + abs(ally[1] - (y_max / 2)) / y_max)  # takes into
        # account the distance from the center
    if len(humans) == 0:  # forces the groups to merge when no humans left
        result += max(allies.values()) - max(enemies.values())
    return result


class AlphabetaThread(Thread):
    def __init__(self, grid):
        """
        Instanciates a thread
        :param grid: the grid representation of the situation
        """
        Thread.__init__(self)
        self.covered_branches = 0
        self.global_move = {}
        self.grid = grid
        self.lock = Lock()
        self.start_time = time.time()
        self.carry_on = True

    def get_next_move_alpha_beta(self, depth, grid):
        """
        Performs the alpha-beta exploration
        :param depth: the exploration depth
        :param grid: the representation of the current grid
        :return: the moves to perform (as a dictionnary)
        """
        return self.alpha_beta_max(depth, grid.humans, grid.allies, grid.enemies, (None, None),
                                   (grid.width, grid.height), True)

    def alpha_beta_max(self, depth, humans, allies, enemies, interval, dimensions, get_moves=False):
        """
        Performs the exploration when it's max' turn
        :param depth: the exploration depth
        :param humans: the humans dictionary
        :param allies: the allies dictionary
        :param enemies: the enemies dictionary
        :param interval: the [alpha, beta] interval as a tuple. None value for a bound means unbounded interval
        :param dimensions: the (x, y) dimension of the grid
        :param get_moves: boolean that tells if the function should return the value of the node (False)
                or the moves (True)
        :return: the value of the node or the moves to perform
        """
        h = heuristic(humans, allies, enemies, False, dimensions[0] - 1, dimensions[1] - 1)
        if depth <= 0:  # if depth is 0, the value is the heuristic
            return h
        else:
            with self.lock:
                if not self.carry_on:  # if the thread should stop now, it does
                    exit()
            children = self.get_relevant_children(humans, allies, enemies, dimensions)  # gets all the relevant
            # children of this situation
            if len(children) == 0:  # if no children are found, returns the heuristic and stops the exploration
                # (or returns no move if get_moves == True)
                if not get_moves:
                    return h
                else:
                    return {}
            hash_code = cache_hash(humans, allies, enemies, depth, True)
            if hash_code in cache:  # if this situation is in cache, just retrieve the associated value or moves
                if get_moves:
                    with self.lock:
                        self.covered_branches = 1  # if get_moves == True (ie if it's the starting node), all the
                        # branches are covered immediately since the situation is already in the cache
                        self.global_move = cache[hash_code][1]
                    return cache[hash_code][1]
                else:
                    return cache[hash_code][0]
            inter = interval
            i = 0
            move = None
            while i < len(children) and (inter[0] is None or inter[1] is None
                                         or inter[0] < inter[1]):  # loops over all the children
                child = children[i]
                i += 1
                if child[4]:  # if the child is probabilistic, just computes the heuristic of that child (no further
                    # exploration)
                    heu = heuristic(child[0], child[1], child[2], True, dimensions[0] - 1, dimensions[1] - 1)
                    val = heu
                else:  # else we continue the exploration
                    if (time.time() - self.start_time) > 0.4 and 1.7 * self.covered_branches / (
                            time.time() - self.start_time) < 1.1:  # if the exploration is late, the depth is reduced
                        # by 2 instead of 1
                        val = self.alpha_beta_min(max(0, depth - 2), child[0], child[1], child[2], inter, dimensions)
                    else:
                        val = self.alpha_beta_min(depth - 1, child[0], child[1], child[2], inter, dimensions)
                if inter[0] is None or (val is not None and val > inter[0]):  # updates the alpha-beta values and the
                    # global_move attribute
                    move = child[3]
                    if get_moves:
                        with self.lock:
                            self.global_move = move
                    inter = (val, inter[1])
                if get_moves:
                    with self.lock:
                        self.covered_branches += 1 / len(children)
            cache[hash_code] = (inter[0], move)  # stores the value and associated move in the cache
            if get_moves:
                return move
            return inter[0]

    def alpha_beta_min(self, depth, humans, allies, enemies, interval, dimensions):
        """
        Performs the exploration when it's min's turn
        :param depth: the exploration depth
        :param humans: the humans dictionary
        :param allies: the allies dictionary
        :param enemies: the enemies dictionary
        :param interval: the [alpha, beta] interval as a tuple. None value for a bound means unbounded interval
        :param dimensions: the (x, y) dimension of the grid
        :return: the value of the node
        """
        h = heuristic(humans, allies, enemies, False, dimensions[0] - 1, dimensions[1] - 1)
        if depth <= 0:
            return h
        else:
            with self.lock:
                if not self.carry_on:
                    exit()
            children = self.get_relevant_children_enemies(humans, allies, enemies, dimensions)
            if len(children) == 0:
                return h
            hash_code = cache_hash(humans, allies, enemies, depth, False)
            if hash_code in cache:
                return cache[hash_code][0]
            inter = interval
            i = 0
            move = None
            while i < len(children) and (inter[0] is None or inter[1] is None
                                         or inter[0] < inter[1]):
                child = children[i]
                i += 1
                if child[4]:
                    heu = heuristic(child[0], child[1], child[2], True, dimensions[0] - 1, dimensions[1] - 1)
                    val = heu
                else:
                    if (time.time() - self.start_time) > 0.1 and 1.7 * self.covered_branches / (
                            time.time() - self.start_time) < 1.1:
                        val = self.alpha_beta_max(max(0, depth - 2), child[0], child[1], child[2], inter, dimensions)
                    else:
                        val = self.alpha_beta_max(depth - 1, child[0], child[1], child[2], inter, dimensions)
                if inter[1] is None or (val is not None and val < inter[1]):
                    move = child[3]
                    inter = (inter[0], val)
            cache[hash_code] = (inter[1], move)
            return inter[1]

    @staticmethod
    def get_relevant_children(humans, allies, enemies, dimensions, is_enemies=False):
        """
        Returns the relevant children list (using defined strategies) from this situation
        :param humans: the humans dictionary
        :param allies: the allies dictionary
        :param enemies: the enemies dictionary
        :param dimensions: the dimensions of the grid
        :param is_enemies: boolean that tells if it's the enemies turn
        :return: a list containing the relevant children
        """
        moves = {ally: set() for ally in allies}
        min_en = min(enemies.values())
        for ally in moves:
            if not is_enemies or allies[ally] >= min_en:  # it's the enemies turn and the enemies group is smaller than
                # the smallest allies group, we skip it
                for strategy in STRATEGIES:  # uses the strategies to get all possible moves for each allies group
                    moves[ally] = moves[ally].union(
                        best_next_move_for_strategy(strategy, ally, humans, allies, enemies, [], dimensions[0] - 1,
                                                    dimensions[1] - 1))
            if len(moves[ally]) == 0:
                moves[ally].add(((ally[0], ally[1], allies[ally]),))  # if no move has been found for that group, we add
                # the "no move" move to the list
        return AlphabetaThread.get_children_from_moves(humans, allies, enemies, moves)  # see under

    @staticmethod
    def get_children_from_moves(humans, allies, enemies, moves):
        """
        Returns the children of this situation given possible moves for each group
        :param humans: the humans dictionary
        :param allies: the allies dictionary
        :param enemies: the enemies dictionary
        :param moves: the moves dictionary for each group
        :return: the children list
        """
        children = []
        i = 0
        corr = {}  # dictionary that maps a number to the position of its moves in moves_for_allies
        moves_for_allies = []  # list of moves for each allies group
        for ally in moves:
            corr[i] = ally
            i += 1
            moves_for_allies.append(moves[ally])
        moves_for_allies = tuple(moves_for_allies)  # converts to a tuple in order to use itertoos.product
        p = set(itertools.product(*moves_for_allies))  # performs the cartesian product of moves
        for moves_set in p:
            if AlphabetaThread.is_actual_move(moves_set, corr):  # check if it's an actual move (ie if at least one
                # group really moves)
                new_humans, new_allies, new_enemies, probabilistic = dict(humans), dict(allies), dict(enemies), False
                # performs a copy of the 3 dictionaries
                for i in range(len(moves_set)):  # see method under
                    probabilistic = probabilistic or AlphabetaThread.get_child_from_move(new_humans, new_allies,
                                                                                         new_enemies, corr[i],
                                                                                         moves_set[i])
                children.append(
                    (new_humans, new_allies, new_enemies, {corr[i]: moves_set[i] for i in range(len(moves_set))},
                     probabilistic))
        return children

    @staticmethod
    def get_child_from_move(new_humans, new_allies, new_enemies, origin, list_of_moves):
        """
        Updates the situation given a list of moves
        :param new_humans: the humans dictionary
        :param new_allies: the allies dictionary
        :param new_enemies: the enemies dictionary
        :param origin: tuple (x, y) that indicates the origin of the group to move
        :param list_of_moves: the list of moves (tuples like (x_dest, y_dest, nb_to_move))
        :return: a boolean saying if the new situation is probabilistic
        """
        probabilistic = False
        for move in list_of_moves:
            destination = (move[0], move[1])
            number = move[2]
            if number == new_allies[origin]:
                del new_allies[origin]  # removes the entry from the allies dictionary
            else:
                new_allies[origin] -= number  # reduces the value of the group
            if destination in new_humans:
                t = new_humans[destination]
                if number >= new_humans[destination]:  # the humans are converted
                    del new_humans[destination]
                    new_allies[destination] = number + t
                else:  # random battle between allies and humans, probabilistic situation
                    p = number / (2 * t)
                    new_allies[destination] = (p ** 2) * (number + t)
                    new_humans[destination] = ((1 - p) ** 2) * t
                    probabilistic = True
            elif destination in new_allies:  # merges allies group
                new_allies[destination] += number
            elif destination in new_enemies:
                t = new_enemies[destination]
                if number > 1.5 * t:  # enemies are killed
                    del new_enemies[destination]
                    new_allies[destination] = number
                else:  # random battle, probabilistic situation
                    if number == t:
                        p = 0.5
                    elif number < t:
                        p = number / (2 * t)
                    else:
                        p = (number / t) - 0.5
                    new_allies[destination] = (p ** 2) * number
                    new_enemies[destination] = ((1 - p) ** 2) * t
                    probabilistic = True
            else:  # moving allies group to an empty place
                new_allies[destination] = number
        return probabilistic

    @staticmethod
    def is_actual_move(moves_set, corr):
        """
        Tells if a move is an actual one
        :param moves_set: the set of moves as computed with itertools.product
        :param corr: the dictionary that maps the position of a group in moves_set to its position on the grid
        :return: True iff at least one group really moves
        """
        if len(corr) != len(moves_set):
            return False
        for i in range(len(corr)):
            if len(moves_set[i]) == 0 or len(moves_set[i][0]) == 0:
                return False
            if len(moves_set[i]) > 1 or corr[i] != (moves_set[i][0][0], moves_set[i][0][1]):
                return True
        return False

    @staticmethod
    def get_relevant_children_enemies(humans, allies, enemies, dimensions):
        """
        Gets the relevant children when it's the enemy's turn
        :param humans: the humans dictionary
        :param allies: the allies dictionary
        :param enemies: the enemies dictionary
        :param dimensions: the dimensions of the grid
        :return: the relevant children list
        """
        children_wrong_order = AlphabetaThread.get_relevant_children(humans, enemies, allies, dimensions,
                                                                     is_enemies=True)
        # calls get_relevant_children inverting allies and enemies
        children = []
        for child in children_wrong_order:
            children.append((child[0], child[2], child[1], child[3], child[4]))  # inverts allies and enemies again
        return children

    def run(self):
        global DEPTH
        DEPTH = max(1,
                    int(8 - 1.5 * (len(self.grid.allies) + len(self.grid.enemies)) + 0.05 * math.log(1 + len(cache))))
        # changes the exploration depth according to the number of allies, enemies and size of cache
        global STRATEGIES
        if len(self.grid.humans) == 0:
            STRATEGIES = ["final_rounds"]  # changes the strategies list if no humans left
        self.get_next_move_alpha_beta(DEPTH, self.grid)  # performs the exploration
        logging.debug("real decision time: {}".format(time.time() - self.start_time))
