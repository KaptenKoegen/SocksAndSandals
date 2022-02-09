import pygame
import images
from pygame.locals import *

pygame.init()
import playerclasses



class Button():
    """ Handles the basics of creating buttons. """
    FONT = pygame.font.SysFont(None, 45)
    def __init__(self, pos, size, text):
        """ It takes as arguments pos (position of the button on the screen),
            size, color and text.
        """
        self.rect = pygame.Rect([0, 0], size)
        self.pos = pos

        # Text
        self.text = self.FONT.render(text, True, (0, 0, 0))
        self.text_rect = self.text.get_rect()
        self.text_rect.center = self.rect.center = pos

        # Outline
        pos = (pos[0] - 2, pos[1] - 2)
        self.outline = pygame.Rect(pos, (size[0] + 4, size[1] + 4))

    def draw(self, screen):
        """ Call this function to draw and blit a rectangular and
            outlined button on screen.
        """
        # Draw Button + text
        screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    def draw_with_outline(self, screen, color):
        pygame.draw.rect(screen, color, self.outline)
        self.draw(screen)


    def is_clicked(self, event):
        """ This function is called to make the buttons clickable. """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                return self.rect.collidepoint(event.pos)
        return event.type == KEYDOWN and event.key == self.key


class MenuButton(Button):

    def __init__(self, pos, text):
        self.image = images.wood[0].sprite
        super().__init__(pos, [170, 92], text)


class ClassButton():
    RADIUS = 30
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)


    def __init__(self, image, pos, btn_class, selected=False):
        self.image = image
        self.pos = pos
        self.btn_class = btn_class
        self.selected = selected

    def draw(self, screen):
        pygame.draw.circle(screen, (0, 0, 0), self.pos, self.RADIUS)
        pygame.draw.circle(screen, self.RED, self.pos, self.RADIUS, 1)
        self.image.blit(screen, self.pos[0], self.pos[1])

    def select(self, screen):
        pygame.draw.circle(screen, self.GREEN, self.pos, self.RADIUS, 1)

    def un_select(self, screen):
        pygame.draw.circle(screen, self.RED, self.pos, self.RADIUS, 1)

    def mouse_collide(self, pos):
        x1, y1, x2, y2 = pos + self.pos
        return (x1 - x2) ** 2 + (y1 - y2) ** 2 < self.RADIUS ** 2








class ActionButton(Button):
    CD_FONT = pygame.font.SysFont(None, 35)

    def __init__(self, pos, ability, key):
        self.image = images.wood[0].sprite
        super().__init__(pos, [170, 92], ability.name)
        self.ability = ability
        self.key = key

    def draw(self, screen, enemy):
        super().draw(screen)
        text, color = self.ability.get_status_text(enemy), self.ability.get_status_color(enemy)
        text = self.CD_FONT.render(text, False, color)
        rect = text.get_rect()
        rect.centerx = self.pos[0]
        rect.centery = self.pos[1] + 25
        screen.blit(text, rect)
