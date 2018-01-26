# -*- coding: utf-8 -*-
"""
Created on Fri Jan 26 11:37:26 2018

@author: Mr_Mey
"""

import socket


class Connector:
    def __init__(self,port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(("localhost", port))
    
    def send(self):
        