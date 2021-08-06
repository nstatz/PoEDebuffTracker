import cv2
from matplotlib import pyplot as plt
from pynput.keyboard import Key, Controller
import os
import datetime as dt
import numpy as np

#rst syntax guide: https://thomas-cokelaer.info/tutorials/sphinx/docstring_python.html

read_color_method = cv2.IMREAD_GRAYSCALE

#use pyinput for flask

#needs class configreader. config reader adds config to class
class Status():

    def __init__(self, config):
        """
        Constructor function

        :param config: Config Dictionary
        :type config: Dictionary
        """
        config = \
        {
            "type" : "bleed",
            "flask_key" : "1",
            "template_path" : r"C:\Users\Nik\Desktop\Python Projekte\PoEDebuffTracker\resources\debuff_templates\bleed.png",
            "color_method" : "template_path",
            "remove_debuff" : True
        }

        template_path = config["template_path"]
        self.__template_img = cv2.imread(template_path, config["color_method"])
        self.__type == config["type"]
        self.__flask_key = config["flask_key"]
        self.__color_method = config["color_method"]

        self.__remove_ailment = config["remove_ailment"]



    def get_img_part(self, img_big):
        """
        Get Upper Left area of screen (debuffs) and return this part of the screen as a image
        :param img_big: Screenshot of Screen
        :type img_big: np.array

        :return: cut image
        :rtype: np.array
        """

        # in pixels
        height = 200
        width = 550
        if len(img_big.shape) == 3:
            image_small = example_img[0:height, 0:width, :]
        else:
            image_small = example_img[0:height, 0:width]

        return image_small


    def check_ailment(self, current_screen):
        """
        Checks if the ailment type of this class was found

        :param current_screen: Screenshot of current game sequence
        :type current_screen: np.array

        :return: True of ailment was found, False if not. Also return False if ailment should not be removed anyway
        :rtype: Boolean
        """

        if self.__remove_ailment == False:
            return False

        ailment_exists = False
        if self.__color_method == cv2.IMREAD_GRAYSCALE:
            current_screen = cv2.cvtColor(current_screen, cv2.COLOR_BGR2GRAY)

        #Upper left part of screen as np.array
        screen_part = self.get_img_part(current_screen)

        # error occurs if template was not found
        try:
            result = cv2.matchTemplate(example_img, template_img, cv2.TM_CCOEFF_NORMED)
            ailment_exists = True
        except cv2.error as err:
            print(err)
        # min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        return ailment_exists


    def get_action(self):
        """
        Returns Key to pe pressed or False of no action is necessary

        :return: Return key to pe pressed or "-1" if no action is necessary
        :rtype: String
        """
        if self.__remove_ailment == False:
            return "-1"
        return self.__flask_key



resource_dir = os.path.join(os.getcwd(), os.pardir, "resources")
template_dir = os.path.join(resource_dir, "debuff_templates")
example_dir = os.path.join(resource_dir, "example_pictures")

template_img_path = os.path.join(template_dir, "bleed.png")

example_img_path = os.path.join(example_dir, "ailments", "chill" ,"3.png")

# use cv2.IMREAD_GRAYSCALE if possible. Only 1/3 of data compared to color cv2.IMREAD_COLOR


# read images
read_color_method = cv2.IMREAD_GRAYSCALE
# read_color_method = cv2.IMREAD_COLOR
template_img = cv2.imread(template_img_path, read_color_method)
print(template_img.shape)
#h, w = template_img.shape

#cv2.imshow('image', template_img)
#cv2.waitKey()

#gray
read_color_method = cv2.IMREAD_GRAYSCALE
example_img = cv2.imread(example_img_path, read_color_method)
image_small = example_img[0:200, 0:550]

#color
# read_color_method = cv2.IMREAD_COLOR
# example_img = cv2.imread(example_img_path, read_color_method)
# image_small = example_img[0:200, 0:550, :]

#print(type(example_img[0][0][0]))
#print(example_img[0][:500].shape)
#print(np.array(example_img[0][:500]))
#example_img_part = example_img
#print(example_img_part[0][:500].shape)
#example_img_part = np.array([np.array(example_img[0][:500]), np.array(example_img[0][:300])])
# example_img_part[0] = example_img_part[0][:500]
# example_img_part[1] = example_img_part[0][:400]
#print(example_img_part.shape)
# print(example_img[0].shape)
cv2.imshow('image', image_small)
cv2.waitKey()


dt_start= dt.datetime.now()
try:
    result = cv2.matchTemplate(example_img, template_img, cv2.TM_CCOEFF_NORMED)
except cv2.error as err:
    print(err)
min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
dt_end = dt.datetime.now()
print(dt_end-dt_start)

def display_match(result, example_img):
    #blue
    marker_color = (255, 0, 0)
    top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)
    cv2.rectangle(example_img, top_left, bottom_right, color = marker_color,thickness=3)
    plt.subplot(121), plt.imshow(result, cmap='gray')
    plt.title('Matching Result'), plt.xticks([]), plt.yticks([])
    plt.subplot(122), plt.imshow(example_img, cmap='gray')
    plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
    plt.suptitle("TM_CCOEFF_NORMED")
    plt.show()

#display_match(result, example_img)
read_color_method = cv2.IMREAD_GRAYSCALE
print(cv2.IMREAD_GRAYSCALE == read_color_method)

#print(example_img_path)
#print(min_val, max_val, min_loc, max_loc)
#print(template_img)
