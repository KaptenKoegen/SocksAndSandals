import random
import math
from enum import Enum

""" This module contains the logical parts of all the abilities in the game.
"""





class EventType(Enum):
    ANIMATION = 0
    ANIMATION2 = 1
    MOVE = 2
    DMG = 3
    ARROW = 4
    STATUS = 5
    IMAGE = 6
    JUMP = 7


class Event():

    def __init__(self, type, *args, DWE_args=None, wait=0):
        self.type = type
        self.args = args
        self.DWE_args = () if DWE_args is None else DWE_args
        self.wait = wait

    def __str__(self):
        return str(self.type)

class Target(Enum):
    CHEST = 0
    FEET = 1
    HEAD = 2
    MID = 3


#General abilities

class Ability():

    def __init__(self, player, name, cd):
        self.player = player
        self.name = name
        self.CD = cd
        self.rem_cd = -1

    def end_of_turn(self):

        if self.rem_cd == 0:
            self.player.end_of_turns.remove(self.end_of_turn)
        self.rem_cd -= 1

    def perform(self, enemy):
        self.player.end_of_turns.append(self.end_of_turn)
        self.rem_cd = self.CD

    def get_status_text(self, enemy):
        return "Ready" if self.rem_cd == -1 else str(self.rem_cd + 1) + "turn CD"

    def get_status_color(self, enemy):
        return (0, 255, 0) if self.get_status_text(enemy) == "Ready" else (255, 0, 0)

class Move(Ability):

    def __init__(self, player, name, i):
        super().__init__(player, name, 0)
        self.i = i

    def perform(self, enemy):
        super().perform(enemy)
        i = self.i
        if (self.player.x * i < enemy.x * i and
            self.player.x * i + self.player.mob > enemy.x * i - self.player.X_SPACE):
            self.player.x = enemy.x - self.player.X_SPACE * i
        else:
            self.player.x += self.player.mob * i
        self.player.x = min(max(self.player.x, self.player.MIN_X), self.player.MAX_X)
        self.player.events.append(Event(EventType.ANIMATION, "walk"))
        self.player.events.append(Event(EventType.MOVE, "walk", i))

    def get_status_text(self, enemy):
        return "Frozen" if self.player.status == "frozen" else "Ready"


class Jump(Ability):
    def __init__(self, player, name, i):
        super().__init__(player, name, 0)
        self.i = i

    def perform(self, enemy):
        super().perform(enemy)
        self.player.x = max(min(self.player.x + self.player.mob * self.i, self.player.MAX_X), self.player.MIN_X)
        self.player.events.append(Event(EventType.ANIMATION, "jump"))
        self.player.events.append(Event(EventType.JUMP, self.i))

    def get_status_text(self, enemy):
        return "Frozen" if self.player.status == "frozen" else "Ready"

class Attack(Ability):

    def __init__(self, player, name, cd, dmg_fct):
        super().__init__(player, name, cd)
        self.dmg_fct = dmg_fct

    def perform(self, enemy):
        super().perform(enemy)
        player = self.player
        if abs(player.x - enemy.x) <= player.range:
            if random.randint(1, 100) > enemy.dodge:
                if not enemy.block_next:
                    enemy.hp -= self.player.atk
                    return self.player.atk
                enemy.block_next = False
                return -2
            return -1

    def get_status_text(self, enemy):
        status = super().get_status_text(enemy)
        if status == "Ready":
            return "Ready" if abs(self.player.x - enemy.x) <= self.player.range else "Not in Range"
        else:
            return status

class MeleeAttack(Attack):

    def perform(self, enemy):
        dmg = super().perform(enemy)
        self.player.events.append(Event(EventType.ANIMATION, "atk"))
        enemy.events.append(Event(EventType.DMG, dmg, wait=("atk_frame_len", 0)))
        if dmg == -2:
            enemy.events.append(Event(EventType.ANIMATION, "block"))




# Guardian Abilities
class BulkUp(Ability):

    EFFECT_LENGTH = 3
    CD = 5

    def __init__(self, player):
        super().__init__(player, "BulkUp", self.CD)

    def perform(self, enemy):
        super().perform(enemy)
        self.old_hp = self.player.hp
        self.player.hp += 300
        self.player.max_hp += 300
        self.rem_effect_length = self.EFFECT_LENGTH
        self.player.end_of_turns.append(self.end_of_turn1)
        self.player.events.append(Event(EventType.DMG, -300, -300))
        self.player.events.append(Event(EventType.IMAGE, 1.5))


    def end_of_turn1(self):
        if self.rem_effect_length == 0:
            self.player.hp = min(self.old_hp, self.player.hp)
            self.player.max_hp -= 300
            self.player.end_of_turns.remove(self.end_of_turn1)
            dmg = self.old_hp + 300 - self.player.hp
            self.player.events.append(Event(EventType.DMG, dmg, 300))
            self.player.events.append(Event(EventType.IMAGE, 1))
        self.rem_effect_length -= 1


class Parry(Ability):

    def __init__(self, player):
        super().__init__(player, "Parry", 2)

    def perform(self, enemy):
        super().perform(enemy)
        self.player.block_next = True
        self.player.events.append(Event(EventType.ANIMATION2, 0))


# Ranger abilities
class RangedAttack(Attack):

    def __init__(self, player, name, cd, dmg_fct=1, arrow=1, degree=1, targets=[Target.CHEST], effect=None):
        super().__init__(player, name, cd, dmg_fct)
        self.arrow = arrow
        self.degree = degree
        self.effect = effect
        self.targets = targets

    def perform(self, enemy):
        dmg = super().perform(enemy)
        self.player.events.append(Event(EventType.ANIMATION, "atk"))
        self.player.events.append(Event(EventType.ARROW, self.degree, self.arrow, dmg, self.effect, self.targets))

class FrostShot(RangedAttack):

    def __init__(self, player):
        DMG_FCT = 0.8
        CD = 3
        IMAGE_ID = 0
        DEGREE = 1
        super().__init__(player, "FrostShot", CD, DMG_FCT, IMAGE_ID, 1, [Target.FEET], "frozen")

    def perform(self, enemy):
        super().perform(enemy)
        def end_of_turn():
            enemy.status = None
            enemy.events.append(Event(EventType.STATUS, None))
            enemy.end_of_turns.remove(end_of_turn)

        enemy.status = "frozen"
        enemy.end_of_turns.append(end_of_turn)

class Multishot(RangedAttack):

    def __init__(self, player):
        DMG_FCT = 2
        CD = 3
        IMAGE_ID = 1
        DEGREE = 1
        super().__init__(player, "Multishot", CD, DMG_FCT, IMAGE_ID, DEGREE,
                         [Target.FEET, Target.MID, Target.HEAD])
