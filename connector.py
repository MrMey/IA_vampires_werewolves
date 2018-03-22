# -*- coding: utf-8 -*-
"""
Created on Fri Jan 26 11:37:26 2018

@author: Mr_Mey
"""

import socket
import time
import os
import struct
import logging
logging.basicConfig(level = logging.INFO)

class Connector:
    def __init__(self, ip, port, name='paul', timeout = None):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip, port))
        if timeout:
            self.sock.settimeout(timeout)
        self.name = name
        self.connected = True
        
    def stop(self):
        if self.sock:
            self.sock.close()
        self.connected = False
        
    def send(self,trame):
        logging.debug("sending")
        self.sock.send(trame)
    
    def receive(self):
        logging.debug("receiving")
        order = bytes()
        while len(order) < 3:
            order += self.sock.recv(1)
        order = order.decode()
        
        if order in ("MAP","UPD"):
            return self.receive_UPD()
        if order == "SET":
            return self.receive_SET()
        if order == "HUM":
            return self.receive_HUM()
        if order == "HME":
            return self.receive_HME()
        if order == "END":
            return self.receive_END()
        if order == "BYE":
            return self.receive_BYE()
        raise Exception("unknown command")
    
    def receive_SET(self):
        n = int(struct.unpack("1B",self.sock.recv(1))[0])
        m = int(struct.unpack("1B",self.sock.recv(1))[0])
        logging.debug(("SET",(n,m)))
        return ("SET",(n,m))
    
    def receive_HUM(self):
        n = struct.unpack("1B",self.sock.recv(1))[0]
        coord = []
        for _ in range(n):
            coord += [struct.unpack("1B",self.sock.recv(1))[0]]
            coord += [struct.unpack("1B",self.sock.recv(1))[0]]
        logging.debug(("HUM",(n,coord)))
        return ("HUM",(n,coord))

    def receive_HME(self):
        x = struct.unpack("1B",self.sock.recv(1))[0]
        y = struct.unpack("1B",self.sock.recv(1))[0]
        logging.debug(("HME",(x,y)))
        return ("HME",(x,y))
    
    def receive_UPD(self):
        n = struct.unpack("1B",self.sock.recv(1))[0]
        changes = []
        for _ in range(n):
            x = struct.unpack("1B",self.sock.recv(1))[0]
            y = struct.unpack("1B",self.sock.recv(1))[0]
            h = struct.unpack("1B",self.sock.recv(1))[0]
            v = struct.unpack("1B",self.sock.recv(1))[0]
            l = struct.unpack("1B",self.sock.recv(1))[0]
            changes += [x,y,h,v,l]

        return ("UPD",(n,changes))
    
    def receive_END(self):
        self.connected = False
        return ("END")
     
    def receive_BYE(self):
        self.connected = False
        return ("BYE")


if __name__ == "__main__":    
    os.popen("VampiresVSWerewolvesGameServer.exe")
    time.sleep(1)
    connect = Connector("127.0.0.1",5555)
    connect.send("NME".encode()+struct.pack("1B",4)+"paul".encode())
    connect.receive()
    connect.receive()
    connect.receive()
    connect.receive()
    connect.receive()
    connect.stop()