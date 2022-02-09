import os
import json
from images import Image, ImageMap

MAIN_DIR = os.path.split(os.path.abspath(__file__))[0]
def load_file(name):
    file = os.path.join(MAIN_DIR, "Data", name + ".json")
    return file

class Resources():

    def __load_resource(path):
        path = load_file(path)
        with open(path, "r") as file:
            return json.load(file)

    def __load_images(data):
        image_dict = {}
        def create_images(string, offsets):
            right = Image(string, *(offsets[:4:2] + offsets[4:]))
            left = right.flip(*offsets[1:4:2])
            return right, left
        for type in data:
            seq = []
            for image in data[type][1:]:
                if(isinstance(image, list)):
                    img = create_images(image[0], image[1:])
                    seq.append(img)
                else:
                    seq.append(create_images(image, data[type][0]))
            image_dict[type] = seq
        return image_dict

    @staticmethod
    def get_stats(type):
        return Resources.__STATS[type]

    @staticmethod
    def get_image(type, index):
        return Resources.__IMAGES[type][index]

    @staticmethod
    def get_image_data(type, part, i):
        return Resources.__IMAGE_DATA[type][part][i]

    @staticmethod
    def get_image_map_data(type):
        return Resources.__IMAGE_MAP_DATA[type]

    __STATS = __load_resource("class_stats")
    __IMAGES = __load_images(__load_resource("images"))
    __IMAGE_MAP_DATA = __load_resource("image_map_data")
    __IMAGE_DATA = __load_resource("image_data")

def create_image_map(class_, weapon_id, direction, scale=1, color=None):
    d = 0 if direction == "right" else 1
    data = Resources.get_image_map_data(class_)
    image_maps = {}
    for type, seq in data.items():
        new_seq = []
        for i,j,k in seq:
            legs_data = Resources.get_image_data(class_, "legs", j)
            legs = __get_image(legs_data[0], d, "legs", *legs_data[1 + d])
            weapon_data = Resources.get_image_data(class_, "weapons", k)
            w_id = Resources.get_image_data(class_, "weapon_img", weapon_id) + weapon_data[0]
            weapon = __get_image(w_id, d, "weapons", *weapon_data[1 + d])
            body_data = Resources.get_image_data(class_, "body", i)
            body = __get_image(body_data[0], d, "body", *body_data[1 + d])
            image_map = ImageMap(legs, body, weapon).scale(scale)
            image_map.changeColor(color)
            new_seq.append(image_map)
        image_maps[type] = new_seq
    return image_maps

def __get_image(id, d, type, rotate=0, x=0, y=0):
    image = Resources.get_image(type, id)[d]
    image = image.incrementOffset(x, y)
    if (rotate != 0):
        image = image.rotate(rotate)
    return image

if __name__ == '__main__':
    print(Resources.get_image_map_data("guardian"))
