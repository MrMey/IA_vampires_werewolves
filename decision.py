# -*- coding: utf-8 -*-
"""
Created on Fri Feb  2 11:29:05 2018

@author: Mr_Mey
"""
import struct
import logging
from time import time,sleep
logging.basicConfig(level = logging.DEBUG)


from algorithm import greedy
from algorithm import splittercell
from algorithm import alphabeta
from algorithm import multisplit

TIME_OUT = 1.5

class Actor:
    def __init__(self, algorithm = 1):
        self.queue = []
        self.algorithm = algorithm
        self.target = []
        self.thread = None
        
    def action(self,grid,turn):
        top = time()
        algorithm = self.algorithm
        if self.algorithm == 5:
            if len(grid.allies) > 3:
                algorithm = 4
            elif len(grid.humans) <= 1:
                algorithm = 2
            elif turn < 3:
                algorithm = 2
            else:
                algorithm = 4
        
        logging.info("choosing algorithm : {}".format(algorithm))
        if algorithm == 4:
            top = time()
            self.thread = multisplit.MultisplitThread(grid)
            self.thread.start()
            sleep(TIME_OUT)
            self.queue = list(self.thread.queue)


        if algorithm == 3:
            top = time()
            self.thread = splittercell.SplittercellThread(grid)
            self.thread.start()
            sleep(TIME_OUT)
            self.queue = list(self.thread.queue)


        elif algorithm == 2:

            self.thread = alphabeta.AlphabetaThread(grid)
            go_on = True
            self.thread.start()
            sleep(TIME_OUT/3)
            with self.thread.lock:
                if self.thread.covered_branches == 0:
                    go_on = False
            if go_on:
                sleep(2*TIME_OUT / 3)
                with self.thread.lock:
                    if len(self.thread.global_move) > 0:
                        dest = dict(self.thread.global_move)
                    else:
                        dest = None
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
            else:
                logging.debug("switching to multisplit")
                del self.thread
                self.thread = None
                temp = self.algorithm
                self.algorithm = 4
                self.action(grid, turn)
                self.algorithm = temp
        logging.debug('turn moves :\n {}'.format(self.queue))


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
        del self.thread
        self.thread = None
