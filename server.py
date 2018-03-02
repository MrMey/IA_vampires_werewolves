import socket

class Server():
    def __init__(self):
        self.ip = "127.0.0.1"
        self.port = 5555

    def start(self):
        self.connexion_principale = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connexion_principale.bind((self.hote, self.port))
        self.connexion_principale.listen(5)

        print("en attente de connexion")

    def connect(self):
        self.connexion_client, self.connexion_infos = self.connexion_principale.accept()
        print("connexion acceptee")