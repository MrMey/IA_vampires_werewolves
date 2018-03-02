# -*- coding: utf-8 -*-
"""
Created on Fri Feb  2 11:29:05 2018

@author: Mr_Mey
"""
import struct
from math import ceil

from algorithm.greedy import get_closest_point, get_distance,get_dest

class Actor:
    def __init__(self, algorithm = 1):
        self.queue = []
        self.algorithm = algorithm
        self.target = []

    def action(self,grid):
        if self.algorithm == 1:
            if len(grid.allies) == 1:
                print("Séparation")
                dest = get_dest(grid, list(grid.allies.keys())[0])
                move = [list(grid.allies.keys())[0][0],list(grid.allies.keys())[0][1],ceil(list(grid.allies.values())[0]/2),dest[0],dest[1]]
                self.queue.append(move)
                grid.add_locked_cell(dest)
            else: 
                print("No separation")
                for ally in grid.allies:
                    print("humans: {}".format(grid.humans))
                    print("allies: {}".format(grid.allies))
                    print("enemies: {}".format(grid.enemies))
                    if self.algorithm == 1:
                        dest = get_dest(grid, ally)

        
                    print("dest : {}".format(dest))
                    move = [ally[0],ally[1],grid.get_group_at(ally[0],ally[1]),dest[0],dest[1]]
                    print("move : {}".format(move))

                    self.queue.append(move)
                    grid.add_locked_cell(dest)
        elif self.algorithm == 2:
            #dest = ...
            pass #to link with alpha beta algo
        

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