# -*- coding: utf-8 -*-
"""
Created on Fri Feb  2 11:29:05 2018

@author: Mr_Mey
"""
import struct
import logging
logging.basicConfig(level = logging.DEBUG)


from algorithm import greedy
from algorithm import splittercell
from algorithm import alphabeta

class Actor:
    def __init__(self, algorithm = 1):
        self.queue = []
        self.algorithm = algorithm
        self.target = []

    def action(self,grid):
        if self.algorithm in [1, 3]:
            for ally in grid.allies:
                logging.debug("humans: {}".format(grid.humans))
                logging.debug("allies: {}".format(grid.allies))
                logging.debug("enemies: {}".format(grid.enemies))
                if self.algorithm == 1:
                    move = greedy.get_dest(grid, ally)
                elif self.algorithm == 3:
                    move = splittercell.get_dest(grid, ally)
                logging.debug("move {}".format(move))
                self.queue += move
        elif self.algorithm == 2:
            dest = alphabeta.get_dest_alpha_beta(grid)
            logging.debug("humans: {}".format(grid.humans))
            logging.debug("allies: {}".format(grid.allies))
            logging.debug("enemies: {}".format(grid.enemies))
            for ally in dest:
                move = [ally[0], ally[1], dest[ally][2], dest[ally][0], dest[ally][1]]
                logging.debug("move {}".format(move))
                self.queue.append(move)


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