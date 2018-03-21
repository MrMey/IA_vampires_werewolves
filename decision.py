# -*- coding: utf-8 -*-
"""
Created on Fri Feb  2 11:29:05 2018

@author: Mr_Mey
"""
import struct
import logging
from time import time
import threading
logging.basicConfig(level = logging.DEBUG)


from algorithm import greedy
from algorithm import splittercell
from algorithm import alphabeta
from algorithm import multisplit

class Actor(threading.Thread):
    def __init__(self, algorithm = 1):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self.queue = []
        self.algorithm = algorithm
        self.target = []

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()
        
    def run(self,grid):
        if self.algorithm in [1, 3, 4]:
            for ally in grid.allies:
                logging.debug("humans: {}".format(grid.humans))
                logging.debug("allies: {}".format(grid.allies))
                logging.debug("enemies: {}".format(grid.enemies))
                if self.algorithm == 1:
                    move = greedy.get_dest(grid, ally)
                elif self.algorithm == 3:
                    move = splittercell.get_dest(grid, ally)
                elif self.algorithm == 4:
                    move = multisplit.get_dest(grid, ally)

                # move must be a list
                self.queue += move
        elif self.algorithm == 2:
            top = time()
            dest = alphabeta.get_dest_alpha_beta(grid)
            logging.debug("humans: {}".format(grid.humans))
            logging.debug("allies: {}".format(grid.allies))
            logging.debug("enemies: {}".format(grid.enemies))
            for ally in dest:
                for destination in dest[ally]:
                    move = [ally[0], ally[1], destination[2], destination[0], destination[1]]
                    logging.debug("move {}".format(move))
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