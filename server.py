
import socket
import random
from _thread import *
import threading
import pickle
from playerclasses import Guardian, Ranger
from battle import Battle
import jsonpickle
import time

server = "192.168.10.231"
port = 7110
UNICODE = 'utf-8'

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen()
print("Waiting for a connection, Server Started")


battle = Battle(Guardian(400, "noggret", 0), Ranger(700, "noggi", 0))
abilities = [255, 255]
lock = threading.Lock()
def threaded_client(player):
    global battle
    global ability
    battle.server_message = player
    conn.send(pickle.dumps(battle))
    battle.server_message = None
    while None in conns:
        pass
    print("both players connected")
    while True:
        recv = conns[player].recv(2048)
        conns[player-1].send(recv)
    conn.close()

currentPlayer = 0
conns = [None, None]
while True:
    conn, addr = s.accept()
    print("Connected to:", addr)
    conns[currentPlayer] = conn
    start_new_thread(threaded_client, (currentPlayer % 2,))
    currentPlayer += 1
    print(conns)
