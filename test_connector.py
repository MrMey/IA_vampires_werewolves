# -*- coding: utf-8 -*-
"""
Created on Fri Jan 26 11:56:26 2018

@author: Mr_Mey
"""

from connector import Connector
import os

def test_creation_socket():
    connect = Connector("127.0.0.1",5555)
    connect.stop()

def test_receive_socket():
    connect = Connector("127.0.0.1",5555)
    connect.receive(1)    
    connect.stop()

def test_NME_order():
    connect = Connector("127.0.0.1",5555)
    connect.send("NME".encode() + "1".encode() + "a".encode())    
    connect.stop()

def test_initiate_order():
    connect = Connector("127.0.0.1",5555)
    connect.send("NME".encode() + "1".encode() + "a".encode())
    connect.receive()
    connect.stop() 



#os.popen("VampiresVSWerewolvesGameServer.exe")
#test_creation_socket()
#test_receive_socket()
test_initiate_order()