# -*- coding: utf-8 -*-
"""
Created on Fri Feb  2 11:29:05 2018

@author: Mr_Mey
"""

from connector import Connector
from grid.grid import Grid
from decision import Actor

import os
import time
import struct


EMULATE_SERVER = True

def execute(name, algorithm = 1):
    """

    :param name: name of the ai
    :param algorithm: 1 for greedy, 2 for alpha-beta
    :return:
    """
    actor = Actor(algorithm)
    conn = Connector("127.0.0.1",5555)

    # envoit sequence NME
    conn.send("NME".encode()+struct.pack("1B",len(name))+name.encode())

    # recoit commande SET
    Set = conn.receive()
    # initialise la carte
    grid = Grid(Set[1][0],Set[1][1])

    # recoit HUM --inutile mais il faut quand même le recevoir
    conn.receive()
    # recoit HME -- utile pour identifier son espèce
    hme = conn.receive()

    #
    Map = conn.receive()
    grid.initiate_all_groups(Map[1],hme[1])
    # tant que la partie est active
    while conn.connected:

        # ecoute le serveur
        order = conn.receive()

        if order[0] == "UPD":
            #update la grille
            grid.update_map(order[1])
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
        time.sleep(0.5)


if __name__ == "__main__":
    if EMULATE_SERVER:
        os.popen("VampiresVSWerewolvesGameServer.exe")
    execute('paul')
