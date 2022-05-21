import pygame
import images
pygame.init()
from pygame.locals import *
screen = pygame.display.set_mode((1080, 800))
import resources
import ai
from battle import Battle
from playerclasses import *
from abilities import EventType, Target
from misc import Animation, HealthBar, Animation2, Arrow
import numpy
from network import Network
from _thread import *

class BattleViewer():

    MAP_SIZE = (2360, 1440)
    FPS = 60
    MODE = "normal" # {normal, network, ai}

    def __init__(self, battle, screen):
        self.screen = screen
        self.scale = 1 # determines the scale of the view. Completely broken atm
        self.clock = pygame.time.Clock()
        self.background = pygame.Surface(self.MAP_SIZE)
        if self.MODE == "network":
            self.network = Network()
            self.battle = self.network.getBattle()
            self.playerID = self.battle.server_message
            if self.playerID == 1:
                start_new_thread(self.listen_server, ())
        else:
            self.battle = battle
            self.network = None
        if self.MODE == "ai":
            self.aiList = [ai.getAI(self.battle.players[0].type), ai.getAI(self.battle.players[1].type)]

        self.players = [self.get_viewer(self.battle.players[0], "left"), self.get_viewer(self.battle.players[1], "right")]
        self.players[0].set_maps(self.players[1])
        self.players[1].set_maps(self.players[0])


    def get_viewer(self, *args):
        return RangedViewer(*args) if args[0].type == "ranger" else RangedViewer(*args)

    def update_screen(self):
        self.screen.fill((0,0,0))
        self.background.blit(images.background, (0, 0))
        self.players[0].draw(self.background, self.scale)
        self.players[1].draw(self.background, self.scale)
        if not self.isAnimating(): # Drawing the turn indicator
            attacker = self.players[self.battle.turn]
            images.gold_arrow.blit(self.background, attacker.x, attacker.y)
        camera_pos = min(max((self.players[0].x + self.players[1].x) / 2, self.screen.get_width() // 2),
                         images.background.get_width() - self.screen.get_width()//2)
        x = - camera_pos  + 1/2 * self.screen.get_width()
        y = - (self.scale - 0.5) * self.background.get_height()
        self.screen.blit(self.background, (x , y))
        pygame.display.flip()

    def isAnimating(self):
        for player in self.players:
            if player.animation is not None or player.animation2 or player.x != player.player.x:
                return True
        return False

    def update(self):
        player1 = self.players[0]
        player2 = self.players[1]
        player1.update()
        player2.update()
        # Swap direction if needed
        if (player1.dir == "left" and player1.x > player2.x or
            player1.dir == "right" and player1.x < player2.x) and not self.isAnimating():
            temp = player1.dir
            player1.dir = player2.dir
            player2.dir = temp
            player1.images = resources.create_image_map(player1.player.type, player1.player.weapon, player1.dir,color=player1.color)
            player2.images = resources.create_image_map(player2.player.type, player2.player.weapon, player2.dir,color=player2.color)
            player1.image = player1.images["walk"][-1]
            player2.image = player2.images["walk"][-1]

    def start(self):
        while True:
            self.update()
            self.update_screen()
            if self.MODE == "ai" and not self.isAnimating() and self.aiList[self.battle.turn] is not None:
                self.battle.perform_ability(self.aiList[self.battle.turn].decideMove(self.battle))
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    quit()
                elif (event.type == KEYDOWN  and not self.isAnimating() and
                      (self.network is None or self.playerID == self.battle.turn)):
                    try:
                        if self.battle.get_ability_status(event.key - K_0 - 1) == "Ready":
                            self.battle.perform_ability(event.key - K_0 - 1)
                            if self.network is not None:
                                self.network.send(event.key - K_0 - 1)
                                start_new_thread(self.listen_server, ())
                    except (IndexError) as e:
                        print("wrong input", e)

            self.clock.tick(self.FPS)


    def listen_server(self):
        ability = self.network.get()
        self.battle.perform_ability(ability)


class PlayerViewer:

    Y = 1400
    walk_frame_len = 4

    def __init__(self, player, dir):
        self.player = player
        self.size = 1
        self.color = None
        self.images = resources.create_image_map(player.type, player.weapon, dir)
        self.dir = dir
        self.image = self.images["walk"][-1]
        self.x = player.x
        self.y =  self.Y
        self.y_func = None
        self.animation = None
        self.animation2 = []
        self.speed = 0
        self.status = None
        self.hp_bar = HealthBar(player.name, player.hp, player.energy)
        for attribute, value in player.STATS.get_stats("animation", player.type).items():
            setattr(self, attribute, value)
        self.walk_frame_len = 4
        self.jump1_frame_len =self.jump_frame_len = 5
        # tuple of (func, *args)
        self.event_map =\
        {EventType.ANIMATION: (self.startAnimation,), EventType.MOVE: (self.set_movement,),
         EventType.ANIMATION2: (self.startAnimation2,), EventType.DMG: (self.deal_dmg,),
         EventType.STATUS: (self.setStatus,), EventType.IMAGE: (self.changeImageMap,),
         EventType.JUMP: (self.jump,)}

    def set_maps(self, enemy):
        self.enemy = enemy

    def draw(self, screen, scale):
        self.image.blit(screen, self.x, self.y, scale, self.blit_prio)
        self.hp_bar.draw(self.x, self.y, screen, scale * self.size)
        if self.status == "frozen": images.ice_block[0].blit(screen, self.x, self.y)
        for animation in self.animation2.copy():
            if not animation.play(screen):
                self.animation2.remove(animation)

    def update(self):
        if self.animation is not None:
            if not self.animation.play(self):
                self.animation = None
        self.x += self.speed
        if abs(self.x - self.player.x) <= abs(self.speed):
            self.x = self.player.x
            self.speed = 0
            self.y =  self.Y
            self.y_func = None
        if self.y_func is not None: self.y  = self.y_func(self.x)
        for event in self.player.events.copy():
            if isinstance(event.wait, tuple):
                event.wait = getattr(self, event.wait[0]) * event.wait[1]
            if event.wait > 0:
                event.wait -= 1
                continue
            func, *args2 = self.event_map[event.type]
            func(event, *args2)
            self.player.events.remove(event)


    def startAnimation(self, event):
        type = event.args[0]
        self.animation = Animation(getattr(self, type+"_frame_len"), type)

    def startAnimation2(self, event):
        length = 60
        animation = Animation2(length, resources.Resources.get_image("icons", event.args[0])[0], (self.x, self.y))
        self.animation2.append(animation)


    def set_movement(self, event):
        self.speed = 7 * event.args[1] * self.player.mob / 100
        if event.args[0] == "jump":
            self.speed = 5 * event.args[1]
            self.y_func = get_parabola_function(self.x, self.player.x, self.y, self.y, 0.02)[0]

    def jump(self, event):
        print(int((self.player.x - self.x )//5))
        self.player.events.append(Event(EventType.MOVE, "jump", event.args[0], wait=self.jump_frame_len*2))
        self.player.events.append(Event(EventType.ANIMATION, "jump1", event.args[0], wait= abs((self.player.x - self.x )//5) + self.jump_frame_len*2))

    def deal_dmg(self, event):
        self.hp_bar.update(self.x, self.y, *event.args)

    def setStatus(self, event):
        self.status = event.args[0]

    def changeImageMap(self, event):
        self.size = event.args[0]
        self.images = resources.create_image_map(self.player.type, self.player.weapon, self.dir, self.size, color=self.color)
        self.image = self.images["walk"][-1]


class RangedViewer(PlayerViewer):

    def __init__(self, player, dir):
        super().__init__(player, dir)
        self.event_map[EventType.ARROW] = (self.spawn_arrow,)

    def spawn_arrow(self, event):
        degree, image, dmg, status, targets = event.args
        for target in targets:
            func = self.get_func(self.x, self.enemy.x, self.y, self.get_target(target), degree)
            self.animation2.append(Arrow(image, self.x, self.enemy.x, func, self.atk_frame_len))
        wait = abs(self.x - self.enemy.x) // Arrow.SPEED + self.atk_frame_len
        self.enemy.player.events.append(Event(EventType.DMG, dmg, wait=wait))
        if status is not None:
            self.enemy.player.events.append(Event(EventType.STATUS, status, wait=wait))
        if dmg == -2:
            wait -= self.enemy.block_frame_len
            self.enemy.player.events.append(Event(EventType.ANIMATION, "block", wait=wait))


    def get_func(self, x1, x2, y1, y2, degree):
        return get_parabola_function(x1, x2, y1, y2, 0.02) if degree == 2 else get_linear_function(x1, x2, y1, y2)

    def get_target(self, target):
        if target == Target.MID: return self.enemy.y + 40
        elif target == Target.FEET: return  self.enemy.y + 100
        elif target == Target.HEAD: return self.enemy.y - 20
        else: return self.enemy.y


def get_parabola_function(x1, x2, y1, y2, a_):
    """ Returns the parabola function that intersects (x1, y1) and (x2, y2)
    with a as a value in (ax^2 + bx + c).
    """
    X = numpy.array([[x1, 1], [x2, 1]])
    a = lambda x: int(a_ * x**2)
    Y = numpy.array([y1 - a(x1), y2 - a(x2)])
    b, c = numpy.linalg.solve(X, Y)
    return lambda x: a(x) + b * x + c, lambda x: 2 * a_ * x + b


def get_linear_function(x1, x2, y1, y2):
    """ Returns the linear function that intersects (x1, y1) and (x2, y2). """
    X = numpy.array([[x1, 1], [x2, 1]])
    Y = numpy.array([y1, y2])
    a, b = numpy.linalg.solve(X, Y)
    return lambda x: a * x + b, lambda x: a


if __name__ == '__main__':
    player1 = Ranger(900, "Kågen", 0)
    player2 = Guardian(1333, "Jolemyr", 0)
    b = Battle(player1, player2)
    battle_viewer = BattleViewer(b, screen)
    battle_viewer.start()
