# IA_vampires_werewolves

##Vue d’ensemble de l’architecture  
Partie connexion : connector.py  
Structure de la carte : grid/grid.py  
Organe de pilotage du choix de l’IA et envoie des mouvements au serveur : decision.py  
Algorithmes d’IA:  
algorithm/greedy.py (not currently working)  
algorithm/alphabeta.py  
algorithm/splittercell.py  (not currently working)  
algorithm/multisplit.py  

## Commandes :
Ci-dessous la ligne de commande à executer:  
python main.py "nom_de_l_ia" algo_id "ip" port

La table de correspondance de l'algo_id est:  
2_ Alpha-bêta  
4_ Multisplit  
5_ Hybride

## Representation de l'environnement
L'objet Grid du module grid.py contient l'environnement à travers les attributs:  
- humans
- allies
- enemies
Il s'agit de trois dictionnaires dont les clés sont les positions et les valeurs sont les nombres d'unités.

## Algorithmes:
Les algorithmes sont stockés dans le dossier /algorithm ils sont instanciés par le module decision.py.
