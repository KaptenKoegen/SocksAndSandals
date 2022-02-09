import pygame
import os
import copy



main_dir = os.path.split(os.path.abspath(__file__))[0]

pygame.display.set_mode()

def load_image(name):
    file = os.path.join(main_dir, "Bilder", name)
    return pygame.image.load(file).convert_alpha()

class ImageMap():

    def __init__(self, legs, body, weapon):
        self.legs = legs
        self.body = body
        self.weapon = weapon

    def scale(self, scale):
        if scale == 1: return self
        return ImageMap(self.legs.scale(scale), self.body.scale(scale), self.weapon.scale(scale))

    def blit(self, screen, x, y, scale=1, blit_prio=["body", "legs", "weapon"]):
        for part in blit_prio:
            getattr(self, part).blit(screen, x, y, scale)

    def flip(self, offset, w_offset=0):
        return (ImageMap(flip(self.legs.sprite, offset, self.legs.y_offset), flip(self.body.sprite, offset, self.body.y_offset),
            flip(self.weapon.sprite, offset + w_offset, self.weapon.y_offset)))

    def changeColor(self, color):
        if color is not None:
            self.legs.changeColor(color)
            self.body.changeColor(color)



class Image():

    def __init__(self, sprite, offset=0, y_offset=None, scale=None):
        if(isinstance(sprite, str)):
            if sprite.find('.') == -1:
                sprite += ".png"
            self.sprite = load_image(sprite);
        else:
            self.sprite = sprite
        self.offset = offset
        if y_offset is None:
            y_offset = -self.sprite.get_height()
        self.y_offset = y_offset
        if scale is not None:
            if isinstance(scale, (float, int)):
                self.sprite = pygame.transform.rotozoom(self.sprite, 0, scale)
                self.offset *= scale
                self.y_offset = self.y_offset * (scale / 2 + 1/2)
            else:
                self.sprite = pygame.transform.scale(self.sprite, scale)
    def rotate(self, angle):
        return Image(pygame.transform.rotate(self.sprite, angle), self.offset, self.y_offset)

    def incrementOffset(self, x, y):
        return Image(self.sprite, x + self.offset, y + self.y_offset)

    def scale(self, scale):
        return Image(pygame.transform.rotozoom(self.sprite, 0, scale), self.offset*scale, self.y_offset*scale)

    def flip(self, x_off=None, y_off=None):
        x_off = self.offset if x_off is None else x_off
        y_off = self.y_offset if y_off is None else y_off
        return Image(pygame.transform.flip(self.sprite, True, False), x_off, y_off)

    def changeColor(self, color):
        for x in range(self.sprite.get_width()):
            for y in range(self.sprite.get_height()):
                r,b,g,a = self.sprite.get_at((x,y))
                if r < 10 and b < 10 and g < 10 and a == 255:
                    self.sprite.set_at((x,y), color)



    def blit(self, screen, x, y, scale=1):
        if scale != 1:
            sprite = pygame.transform.rotozoom(self.sprite, 0, scale)
            offset = self.offset * scale
            y *= scale
            x *= scale
        else:
            sprite = self.sprite
            offset = self.offset
        p = x + offset, y + self.y_offset * scale
        screen.blit(sprite, p)
        rect = sprite.get_rect()
        rect.topleft = p
        #pygame.draw.rect(screen, (0,0,0), rect,1)


def flip(image, offset=0, y_offset=0):
    return Image(pygame.transform.flip(image, True, False), offset, y_offset)

def flip_all(dict, offsets):
    flipped = {}
    for key, images in dict.items():
        seq = []
        for image_map in images:
            offset = offsets.pop(0)
            seq.append(image_map.flip(offset))
        flipped[key] = seq
    return flipped

def resize(image, x, y, offset, y_offset=0):
    return Image(pygame.transform.scale(image, (x, y)), offset, y_offset)

def bulk_up(image, offset):
    return resize(image, 372, 423)

from resources import Resources
ice_block = Resources.get_image("other", 0)
gold_arrow = Resources.get_image("background", 3)[0]
menu_back = load_image("background.png")
wood = Resources.get_image("background", 1)
background = load_image("bild1.png")




if __name__ == "__main__":
    print(3)
