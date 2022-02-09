from abilities import *
import os
import json



class PlayerStats():

    PATH = os.path.join(os.path.split(os.path.abspath(__file__))[0], "Data", "class_stats.json")

    def __init__(self):
        with open(self.PATH, 'r') as file:
            self.__stats = json.load(file)

    def get_stats(self, type, class_):
        """class: [Guardian, Ranger ...],
           type: [stats, animation]
        """
        return self.__stats[class_][type]


if __name__ == '__main__':
    with open(PlayerStats.PATH, 'w') as file:
        json.dump(d, file, indent=4)


class Player:

    X_SPACE = 120
    MAX_X = 2260
    MIN_X = 100
    STATS = PlayerStats()

    def __init__(self, x, name, type, weapon, increments={}):
        for attribute, value in self.STATS.get_stats("stats", type).items():
            if attribute in increments:
                setattr(self, attribute, value + increments[attribute])
            else:
                setattr(self, attribute, value)
        # hp, atk, dodge, range, mob loaded from json_file
        self.x               = x
        self.name            = name
        self.type            = type
        self.weapon          = weapon
        self.max_hp          = self.hp
        self.max_energy      = self.energy
        self.block_next      = False
        self.status          = None
        self.end_of_turns    = []
        self.events          = []
        self.abilities = [Move(self, "Move Left", -1), Jump(self, "Jump Left", -1),
                          Jump(self, "Jump Right", 1), Move(self, "Move Right", 1)]

    def trigger_end_of_turn(self):
        list_copy = self.end_of_turns.copy()
        for end_of_turn in list_copy:
            end_of_turn()


class Guardian(Player):

    def __init__(self, x, name, weapon):
        super().__init__(x, name, "guardian", weapon)
        self.abilities += [MeleeAttack(self, "Attack", 0, 1), Parry(self),
                           BulkUp(self)]

class Ranger(Player):

    def __init__(self, x, name, weapon):
        super().__init__(x, name, "ranger", weapon)
        self.abilities += [RangedAttack(self, "Attack", 0),
                           FrostShot(self), Multishot(self)]
