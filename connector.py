# -*- coding: utf-8 -*-
"""
Created on Fri Jan 26 11:37:26 2018

@author: Mr_Mey
"""

import socket
import time
import os

class Connector:
    def __init__(self,ip,port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip, port))
        self.sock.settimeout(10)
        print(self.sock)

    def stop(self):
        if self.sock:
            self.sock.close()

    def send(self,trame):
        print("sending")
        self.sock.send(trame)
    
    def receive(self):
        print("receiving")
        order = bytes()
        while len(order) < 3:
            order += self.sock.recv(1)
        order = order.decode()
        
        if order in ["MAP","UPD"]:
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
        n = self.sock.recv(1).decode()
        m = self.sock.recv(1).decode()
        print(("SET",(n,m)))
        return ("SET",(n,m))
    
    def receive_HUM(self):
        n = int(self.sock.recv(1).decode())
        coord = []
        for i in range(n):
            coord += [int(self.sock.recv(1).decode())]
            coord += [int(self.sock.recv(1).decode())]
        print(("HUM",(n,coord)))
        return ("HUM",(n,coord))

    def receive_HME(self):
        x = int(self.sock.recv(1).decode())
        y = int(self.sock.recv(1).decode())
        print(("HME",(x,y)))
        return ("HME",(x,y))
    
    def receive_UPD(self):
        n = int(self.sock.recv(1).decode())
        changes = []
        for i in range(n):
            x = int(self.sock.recv(1).decode())
            y = int(self.sock.recv(1).decode())
            h = int(self.sock.recv(1).decode())
            v = int(self.sock.recv(1).decode())
            l = int(self.sock.recv(1).decode())
            changes += [(x,y,h,v,l)]
        print(("UPD",(n,changes)))
        return ("UPD",(n,changes))
    
    def receive_END(self):
        return ("END")
     
    def receive_BYE(self):
        return ("BYE")
        
    
if __name__ == "__main__":    
    #os.popen("VampiresVSWerewolvesGameServer.exe")
    time.sleep(1)
    connect = Connector("127.0.0.1",5555)
    time.sleep(1)
    connect.send("NME4paul".encode())
    time.sleep(1)
    connect.receive()
    connect.receive()
    connect.receive()
    connect.receive()
    connect.stop() 

