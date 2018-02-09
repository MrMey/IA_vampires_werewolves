# coding: utf8

import main
import os
import time
import re

from threading import Thread

ai_list = {'1': {'name': 'paul',
                 'strategy': 'greedy'},
           '2': {'name': 'jean',
                 'strategy': 'greedy'}
           }


class AiThread(Thread):
    def __init__(self,name):
        Thread.__init__(self)
        self.name = name

    def run(self):
        main.execute(self.name)

def analyse_games(ai1,ai2,log_list):

    for file in log_list:
        with open(file, 'r') as f:
            lines = f.readlines()
            lines = lines[-4:]
            lines = re.findall('car (.*).', lines[1])[0]

            with open('result.csv','a') as f:
                f.write(ai1 + ';' + ai2 + ';')
                if re.search("Werewolves", lines) and re.search("trichÃ©", lines):
                    f.write('0;1\n')
                if re.search("Vampires", lines) and re.search("trichÃ©", lines):
                    f.write('1;0\n')





for ai1 in ai_list:
    for ai2 in ai_list:
        print(ai1,ai2)
        old_files = os.listdir(os.getcwd())
        os.popen("VampiresVSWerewolvesGameServer.exe")
        thread1 = AiThread(ai_list[ai1]['name'])
        thread2 = AiThread(ai_list[ai2]['name'])

        thread1.start()
        thread2.start()

        time.sleep(5)
        os.system("TASKKILL /F /IM VampiresVSWerewolvesGameServer.exe")
        new_files = [x for x in os.listdir(os.getcwd()) if x not in old_files]
        analyse_games(ai_list[ai1]['name'],ai_list[ai2]['name'],new_files)
