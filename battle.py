from playerclasses import Guardian
import jsonpickle
from network import Network
class Battle():

    def __init__(self, player1, player2):
        self.turn = 0
        self.players = [player1, player2]

    def get_ability_status(self, ability_index):

        return self.players[self.turn].abilities[ability_index].get_status_text(self.players[self.turn-1])

    def perform_ability(self, ability_index):
        if ability_index != -1:
            self.players[self.turn].abilities[ability_index].perform(self.players[self.turn-1])
        self.players[self.turn].trigger_end_of_turn()
        self.turn = (self.turn + 1) % 2

    def get_player(self):
        return self.players[self.turn]


if __name__ == '__main__':
    player1 = Guardian(100, "1", 0)
    player2 = Guardian(220, "2", 0)
    n= Network()
    b = n.getBattle()
    id = b.server_message
    while True:
        if id == b.turn:
            x = eval(input("input abilioty number"))
            if b.get_ability_status(x) == "Ready":
                print("player", b.turn, "used ability", player1.abilities[x].name)
                b.perform_ability(x)
                n.send(x)
            else:
                print(b.get_ability_status(x))
        else:
            ability = n.get()
            print("recieved ability ", ability)
            b.perform_ability(ability)
