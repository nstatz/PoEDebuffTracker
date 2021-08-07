import cv2
from pynput.keyboard import Key, Controller
import os
import datetime as dt
import numpy as np
from debufftracker import errors as customErrors
import threading

# class inherits from threading.Thread, so that multiple instances can run in parallel
class Status(threading.Thread):

    def __init__(self, config):
        """
        Constructor function

        :param config: Config Dictionary
        :type config: Dictionary
        """
        # config example
        # config = \
        # {
        #     "type" : "bleed",
        #     "flask_key" : "1",
        #     "color_type" : "gray",
        #     "remove_debuff" : True
        # }
        threading.Thread.__init__(self)
        self.__type = config["type"]
        self.__flask_key = config["key"]
        self.__remove_ailment = config["remove_debuff"]

        # color method to read template. Must match color method used to grab the screenshot
        #self.__color_method = cv2.IMREAD_GRAYSCALE # grayscale doesn't work -> Same templates, different color
        if config["color_type"] == "color":
            self.__color_method = cv2.IMREAD_COLOR

        template_path = os.path.join(os.getcwd(), os.pardir, "resources", "debuff_templates" , f"{self.__type}.png")
        file_exists = os.path.exists(template_path)
        if file_exists == False:
            raise customErrors.FileConfigError(template_path)
        self.__template_img = cv2.imread(template_path, self.__color_method)

        self.__keyboad = Controller()


    def run(self, current_screen):
        """
        Overwrites run function from threading.Thread

        :param current_screen: partial screenshot of upper left area
        :type current_screen: np.array

        :return: empty dict if no action, action_dict if debuff was removed
        :rtype: dict
        """
        effect_exists = self.check_ailment(current_screen)
        if effect_exists == False:
            return {}

        if effect_exists == True:
            self.perform_action()
        action_dict = {"type": self.__type, "key_pressed": self.__flask_key, "dt": dt.datetime.now()}
        return action_dict


    def check_ailment(self, current_screen, show_match=False):
        """
        Checks if the ailment type of this class was found

        :param current_screen: Screenshot of current game sequence
        :type current_screen: np.array

        :param show_match: Parameter to force show a match. Only for debugging purposes
        :type show_match: Boolean

        :return: True of ailment was found, False if not.
        :rtype: Boolean
        """

        ailment_exists = False
        # max value of normed methods return -1 to 1. They are slightly less performant,
        # but interpretability is much easier. List of all options:
        # https://docs.opencv.org/4.5.2/d4/dc6/tutorial_py_template_matching.html
        result = cv2.matchTemplate(current_screen, self.__template_img, cv2.TM_CCORR_NORMED)

        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if max_val >= 0.95:
            ailment_exists = True

        if show_match == True:
            height, width, d = self.__template_img.shape
            top_left = max_loc
            bottom_right = (top_left[0] + width, top_left[1] + height)
            cv2.rectangle(current_screen, top_left, bottom_right, (0, 0, 255), 4)

            cv2.imshow('status.py', current_screen)
            cv2.waitKey()

        return ailment_exists


    def perform_action(self):
        """
        Returns True / False wether or not the flask_key was pressed

        :return: if flask_key was pressed
        :rtype: Boolean
        """
        if self.__remove_ailment == False:
            return False

        self.__keyboad.press(self.__flask_key)
        self.__keyboad.release(self.__flask_key)
        print(f"pressed {self.__flask_key} to remove {self.__type}")
        return True

# just for seperate Tests. This won't be executed, when imported externally
# will be removed once Tool is completed
if __name__ == "__main__":
    resource_dir = os.path.join(os.getcwd(), os.pardir, "resources")
    example_dir = os.path.join(resource_dir, "example_pictures")
    example_img_path = os.path.join(example_dir, "ailments", "chill", "11.png")

    #template_img_path = os.path.join(template_dir, "chill.png")

    #read_color_method = cv2.IMREAD_GRAYSCALE
    read_color_method = cv2.IMREAD_COLOR
    #template_img = cv2.imread(template_img_path, read_color_method)
    example_img = cv2.imread(example_img_path, read_color_method)

    config = \
        {
            "type" : "chill",
            "key" : "1",
            "color_type" : "color",
            "remove_debuff" : True
        }
    status_chill = Status(config)
    result = status_chill.check_ailment(example_img, show_match=True)
    print(result)


