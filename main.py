# -*- coding: utf-8 -*-
"""
Created on Fri Feb  2 11:29:05 2018

@author: Mr_Mey
"""
import os
import time
import struct
import sys
import threading
import logging
logging.basicConfig(level = logging.DEBUG)

from connector import Connector
from grid.grid import Grid
from decision import Actor


EMULATE_SERVER = True
TIME_OUT = 1

def execute(name, algorithm, ip, port):
    print(ip, port)
    """

    :param name: name of the ai
    :param algorithm: 1 for greedy, 2 for alpha-beta
    :return:
    """
    actor = Actor(algorithm)
    conn = Connector(ip, port)

    # envoie sequence NME
    conn.send("NME".encode()+struct.pack("1B",len(name))+name.encode())

    # recoit commande SET
    Set = conn.receive()
    # initialise la carte
    grid = Grid(Set[1][0],Set[1][1])

    # recoit HUM —inutile mais il faut quand même le recevoir
    conn.receive()
    # recoit HME — utile pour identifier son espèce
    hme = conn.receive()

    #
    Map = conn.receive()
    grid.initiate_all_groups(Map[1],hme[1])

    turn = 0
    # tant que la partie est active
    while conn.connected:

        # écoute le serveur
        logging.info('starting turn {}'.format(turn))
        order = conn.receive()
        start_time = time.time()

        if order[0] == "UPD":
            #update la grille
            grid.update_map(order[1])
        elif order[0] == "BYE":
            # TODO clean break
            logging.error("server unexpectedly close connexion")
            break
        elif order[0] == "END":
            logging.info("finishing game")
            # TODO clean break
            break

        # prend la decision
        actor.action(grid, turn)

        # envoie file d'actions au serveur
        conn.send(actor.send_moves())

        logging.info('finishing turn {} \n elapsed time : {}s'.format(turn, time.time()-start_time))

        # vide la file d'action pour prochain tour
        actor.clean_moves()


        # attend une seconde pour visualiser sur .exe


        #time.sleep(0.5)

        turn += 1



if __name__ == "__main__":
    args = sys.argv
    execute(name = args[1], algorithm = int(args[2]), ip = args[3], port = int(args[4]))

