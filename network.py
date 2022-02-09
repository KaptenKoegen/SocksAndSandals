import socket
import jsonpickle
import pickle
UNICODE = 'utf-8'

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "192.168.10.231"
        self.port = 7110
        self.addr = (self.server, self.port)
        self.connect()



    def connect(self):
        try:
            self.client.connect(self.addr)
        except:
            pass

    def get(self):
        try:
            return int.from_bytes(self.client.recv(2048), "big")
            return jsonpickle.decode(self.client.recv(2048))
        except Exception as e:
            #print(e)
            return None

    def getBattle(self):
        return pickle.loads(self.client.recv(2048))

    def send(self, data):
        try:
            self.client.send(bytes([data]))
            #self.client.send(jsonpickle.encode(data).encode(UNICODE))
            #return jsonpickle.encode(self.client.recv(2048))
        except Exception as e:
            print(e)
