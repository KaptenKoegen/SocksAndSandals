import pygame
from pygame.locals import *


pygame.init()

import images
from buttons import MenuButton, ClassButton
from playerclasses import Ranger, Guardian

class Menu():

    def __init__(self, screen):
        self.screen = screen

    def main(self):
        self.screen.blit(images.background, (0,0))
        play_btn = MenuButton([590, 500], "Play")
        play_btn.draw(self.screen)
        pygame.display.flip()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    quit()
                if play_btn.is_clicked(event):
                    pass
                    running = False

    def character_selection(self):
        surfaces = [pygame.Surface((540, 400)), pygame.Surface((540,400))]
        for y in range(12):
            for x in range(0, 12, 1):
                images.wood[x%2].blit(self.screen, x * 170, y * 92)
        play_btn = MenuButton([995, 754], "Play")
        play_btn.draw(self.screen)
        pygame.display.flip()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if play_btn.is_clicked(event): return

if __name__ == '__main__':
    menu = Menu(pygame.display.set_mode((1080, 800)))
    menu.main()
    menu.character_selection()
