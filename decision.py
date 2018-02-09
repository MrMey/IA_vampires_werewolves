# -*- coding: utf-8 -*-
"""
Created on Fri Feb  2 11:29:05 2018

@author: Mr_Mey
"""
import struct
from .algorithm.greedy import get_closest_point

class Actor:
    def __init__(self, algorithm = 1):
        self.queue = []
        self.algorithm = algorithm
        
    def action(self,grid):
        for ally in grid.allies:
            print("humans: {}".format(grid.humans))
            print("allies: {}".format(grid.allies))
            print("ennemies: {}".format(grid.ennemies))
            if self.algorithm == 1:
                dest = get_closest_point(grid,ally,grid.humans[0],True)
            elif self.algorithm == 2:
                #dest = ...
                pass #to link with alpha beta algo
            print("dest : {}".format(dest))
            move = [ally[1],ally[0],grid.get_group_at(ally[1],ally[0]).number,dest[1],dest[0]]
            print("move : {}".format(move))
            self.queue.append(move)
            
    def send_moves(self):
        paquet = bytes()
        paquet += 'MOV'.encode()
        paquet += struct.pack('b', len(self.queue))
        for move in self.queue:
            for el in move:
                paquet += struct.pack('b', el)
        return paquet

    def clean_moves(self):
        self.queue = []