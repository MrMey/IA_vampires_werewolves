import struct

import Grid


# Trame to action
def trame_to_action(trame):
	"""Reçoit un tuple de type : ('SET', '1', '3')"""

	ordre = trame[0]
	args = trame[1:]

	if ordre == 'SET':		# args = (n, m)
		initialize(args) 
	elif ordre == 'HUM':	# args = (n, x, y, x', y', ...)
		setHum(args) 	 
	elif ordre == 'HME': 	# args = (x, y)
		setHome(args)
	elif ordre == 'MAP': 	# args = (n, x, y, H, V, W, ...)
		setMap()
	elif ordre == 'UPD':	# args = (n, x, y, H, V, W, ...)
		updateMap(args)
	elif ordre == 'END':	# args = None
		end()
	elif ordre == 'BYE':	# args = None
		bye()


def initalize(content):
	grid = Grid(int(content[0]), int(content[1]))

def setHum(content):
	n = content[0]
	liste = [ int(x) for x in content[1:] ]
	for i in range(0, n, 2):
		grid.addHum(liste[i], liste[i+1])

def setHome(content):
	grid.addHome(int(content[0]), int(content[1]))

def setMap(content):
	n = content[0]
	liste = [ int(x) for x in content[1:] ]
	for i in range(0, n, 5):
		position = [ int(x) for x in liste[i:i+6] ]
		grid.setPosition(position)

def updateMap(content):
	n = content[0]
	liste = [ int(x) for x in content[1:] ]
	for i in range(0, n, 5):
		position = [ int(x) for x in liste[i:i+6] ]
		grid.updatePosition(position)

def end():
	grid.end()

def bye():
	grid.bye()


# Action to trame
def action_to_trame(action, args):
	if action == 'name':	
		send_name(args)			# args = name
	elif action == 'move':						
		send_moves(args)		# args = [x, y, N, x', y', ...]

def send_name(name):
	paquet = bytes()
	paquet += 'NME'.encode()
	paquet += struct.pack('b', len(name))
	paquet += name.encode()
	return paquet

def send_moves(liste):
	paquet = bytes()
	paquet += 'MOV'.encode()
	paquet += struct.pack('b', len(liste))
	for el in liste:
		paquet += struct.pack('b', el)
	return paquet