# -*- coding: utf-8 -*-
"""
Created on Fri Feb  2 11:29:05 2018

@author: Mr_Mey
"""

from connector import Connector
from grid.grid import Grid
from .decision import Actor

import os
import time
import struct


#Set parameter for actions : 1 for greedy, 2 for alpha-beta
algorithm = 1

actor = Actor(algorithm)

os.popen("VampiresVSWerewolvesGameServer.exe")

name = 'paul'

conn = Connector("127.0.0.1",5555)

# envoit sequence NME
conn.send("NME".encode()+struct.pack("1B",len(name))+name.encode())

# recoit commande SET
Set = conn.receive()
# initialise la carte
grid = Grid(Set[1][0],Set[1][1])

# recoit HME --inutile mais il faut quand même le recevoir
conn.receive()
# recoit HME --inutile mais il faut quand même le recevoir
conn.receive()

# 
Map = conn.receive()
grid.update_all_groups(Map[1])

# tant que la partie est active
while conn.connected:
    
    # ecoute le serveur
    order = conn.receive()
    if order[0] == "UPD":
        #update la grille
        grid.update_all_groups(order[1])
        print("map {}".format([grid.height,grid.width]))
    elif order[0] == "BYE":
        # to do clean break
        break
    elif order[0] == "END":
        # to do clean break
        break
    
    # take decision
    actor.action(grid)
    
    # envoyer file d'actions au serveur
    conn.send(actor.send_moves())
    # vider la file d'action pour prochain tour
    actor.clean_moves()
    # attendre une seconde pour visualiser sur .exe
    time.sleep(2)



