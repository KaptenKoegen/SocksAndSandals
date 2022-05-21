import pygame
import images
import resources
import math


class Animation():

    def __init__(self, frame_length, type):
        self.frame_length = frame_length
        self.frame        = 0
        self.type         = type

    def play(self, player):
        for i in range(len(player.images[self.type])):
            if self.frame == i * self.frame_length:
                player.image = player.images[self.type][i]
                if i == len(player.images[self.type]) - 1:
                    return False
        self.frame += 1
        return True
class Animation2():

    def __init__(self, length, image, p):
        self.frame = length
        self.image = image
        self.p = p

    def play(self, screen):
        self.frame -= 1
        self.image.blit(screen, self.p[0], self.p[1])
        return self.frame > 0

class DamageAnimation(Animation2):

    LENGTH = 15
    FONT = pygame.font.SysFont(None, 35)
    def __init__(self, dmg, p, offset):
        if dmg == -1:
            string = "Miss"
            color = (255, 255, 255)
        elif dmg == -2:
            string = "Block"
            color = (170, 170, 170)
        else:
            string = str(-dmg)
            if dmg > 0: color = (255, 0, 0)
            else:
                color = (0, 255, 0)
                string = "+" + string
        text = self.FONT.render(string, True, color)
        text_rect = text.get_rect()
        text_rect.center = p
        super().__init__(self.LENGTH, images.Image(text, y_offset=offset), text_rect)

class Arrow():

    SPEED = 10

    def __init__(self, image, x1, x2, y_func, delay):
        self.x = x1
        self.x2 = x2
        self.y_func = y_func[0]
        self.derivative = y_func[1]
        self.y = self.y_func(x1)
        self.delay = delay
        self.image = resources.Resources.get_image("arrows", image)[0]
        self.dir = 1 if x2 > x1 else -1

    def play(self, screen):
        self.delay -= 1
        if self.delay <= 0:
            self.x += self.dir * self.SPEED
            self.y = self.y_func(self.x)
        image = self.image.rotate(-math.degrees(math.asin(self.derivative(self.x))) + 90 *(self.dir+1))
        image.blit(screen, self.x, self.y)
        return abs(self.x - self.x2) >= self.SPEED





class HealthBar:

    WIDTH = 80
    HEIGHT = 15
    GRAY = (90, 90, 90)
    RED = (220, 20, 20)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    BLUE = (20, 20, 255)
    OFFSET = - 258
    NAME_OFFSET = -30
    DMG_OFFSET = OFFSET + 30
    TEXT_SIZE = 21
    NAME_SIZE = 30

    def __init__(self, name, hp, energy):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.energy = energy
        self.max_energy = energy
        self.dmg_text = None

    def update(self, x, y, dmg, max_hp_dmg=0):
        if dmg not in (-1,-2): self.hp -= dmg
        self.max_hp -= max_hp_dmg
        self.dmg_text = DamageAnimation(dmg, (x, y), self.DMG_OFFSET)

    def draw_bar(self, x, y, screen, scale, stat, max, color):
        outline = pygame.Rect(0, 0, self.WIDTH * scale + 4, self.HEIGHT * scale + 4)
        gray_bar = pygame.Rect(0, 0, self.WIDTH * scale, self.HEIGHT * scale)
        outline.center = (x, y + self.OFFSET * scale)
        gray_bar.center = outline.center
        red_bar = pygame.Rect(0, 0, self.WIDTH * (stat / max) * scale, self.HEIGHT * scale)
        red_bar.topleft = gray_bar.topleft

        # Health Text
        font = pygame.font.SysFont(self.name, round(self.TEXT_SIZE * scale), True)
        text = font.render(str(stat) + "/" + str(max), True, self.BLACK)
        text_rect = text.get_rect()
        text_rect.center = gray_bar.center

        # Drawing
        pygame.draw.rect(screen, self.BLACK, outline)
        pygame.draw.rect(screen, self.GRAY, gray_bar)
        pygame.draw.rect(screen, color, red_bar)
        screen.blit(text, text_rect)
        return text_rect


    def draw(self, x, y, screen, scale):
        #HealthBar
        text_rect = self.draw_bar(x, y, screen, scale, self.hp, self.max_hp, self.RED)
        self.draw_bar(x, y + self.HEIGHT * scale, screen, scale, self.energy, self.max_energy, self.BLUE)

        name_font = pygame.font.SysFont(self.name, round(self.NAME_SIZE * scale), False)
        name_text = name_font.render(self.name, True, self.WHITE)
        name_text_rect = name_text.get_rect()
        name_text_rect.center = text_rect.centerx, text_rect.centery + self.NAME_OFFSET * scale
        screen.blit(name_text, name_text_rect)

        if self.dmg_text is not None and not self.dmg_text.play(screen):
            self.dmg_text = None
