# -*- coding: utf-8 -*-
"""
Created on Fri Feb  2 11:29:05 2018

@author: Mr_Mey
"""
import struct
import logging
from time import time
logging.basicConfig(level = logging.DEBUG)


from algorithm import greedy
from algorithm import splittercell
from algorithm import alphabeta
from algorithm import multisplit

class Actor:
    def __init__(self, algorithm = 1):
        self.queue = []
        self.algorithm = algorithm
        self.target = []
        
    def action(self,grid,turn):
        algorithm = self.algorithm
        if self.algorithm == 4:
            if len(grid.humans) <= 1:
                algorithm = 2
            elif turn < 3:
                algorithm = 2
        
        print(sum(grid.allies.values()))
        print(sum(grid.enemies.values()))
        print(len(grid.enemies))
        if sum(grid.allies.values()) < sum(grid.enemies.values()) and len(grid.humans) == 0 and len(grid.enemies) == 1:
            algorithm = 3

        logging.info("choosing algorithm : {}".format(algorithm))
        if algorithm == 4:
            top = time()
            thread = multisplit.MultisplitThread(grid)
            thread.start()
            thread.join(1.7)
            self.queue = thread.queue
            del thread

        if algorithm == 3:
            top = time()
            thread = splittercell.SplittercellThread(grid)
            thread.start()
            thread.join(1.7)
            self.queue = thread.queue
            del thread

        elif algorithm == 2:
            top = time()
            thread = alphabeta.AlphabetaThread(grid)
            thread.start()
            thread.join(1)
            dest = thread.global_move
            del thread

            logging.debug("humans: {}".format(grid.humans))
            logging.debug("allies: {}".format(grid.allies))
            logging.debug("enemies: {}".format(grid.enemies))
            logging.debug("dest: {}".format(dest))

            if dest is not None:
                for ally in dest:
                    for destination in dest[ally]:
                        move = [ally[0], ally[1], destination[2], destination[0], destination[1]]
                        if abs(move[0] - move[3]) > 1 or abs(move[1] - move[4]) > 1 or destination[2] > grid.allies[ally]:
                            logging.debug("ERROR!!!")
                        logging.debug("move {}".format(move))
                        if not (ally[0] == destination[0] and ally[1] == destination[1]):
                            self.queue.append(move)
            logging.debug("decision duration: {}".format(time() - top))


    def send_moves(self):
        paquet = bytes()
        paquet += 'MOV'.encode()
        paquet += struct.pack('B', len(self.queue))
        for move in self.queue:
            for el in move:
                # need to use usigned byte to go up to 255 units
                paquet += struct.pack('B', el)
        return paquet

    def clean_moves(self):
        self.queue = []