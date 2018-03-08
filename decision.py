# -*- coding: utf-8 -*-
"""
Created on Fri Feb  2 11:29:05 2018

@author: Mr_Mey
"""
import struct
import logging
logging.basicConfig(level = logging.DEBUG)

from algorithm.greedy import get_dest

class Actor:
    def __init__(self, algorithm = 1):
        self.queue = []
        self.algorithm = algorithm
        self.target = []

    def action(self,grid):
        for ally in grid.allies:
            logging.debug("humans: {}".format(grid.humans))
            logging.debug("allies: {}".format(grid.allies))
            logging.debug("enemies: {}".format(grid.enemies))
            if self.algorithm == 1:
                dest = get_dest(grid, ally)

            elif self.algorithm == 2:
                #dest = ...
                pass #to link with alpha beta algo
            logging.debug("dest : {}".format(dest))
            move = (ally[0], ally[1], grid.get_group_at(ally[0],ally[1]), dest[0], dest[1])
            logging.debug("move : {}".format(move))

            self.queue.append(move)
            grid.add_locked_cell(dest)

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