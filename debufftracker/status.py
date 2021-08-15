import cv2
from pynput.keyboard import Controller
import os
import datetime as dt
from debufftracker import errors as customErrors
import logging

log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logger = logging.getLogger(__name__)
logger.setLevel('INFO')
formatter = logging.Formatter(log_format)

streamHandler = logging.StreamHandler()
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)


# Status class used to inherit from threading.Thread. While this was much more elegant it caused issues being hard to control,
# as Thread.start() was not invoked, but Thread.run(), to be callable multiple times without having the need to create
# the same instance over and over again. Creating new instances of Status is avoidable overhead.
class Status:

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
        #     "key" : "1",
        #     "color_type" : "color",
        #     "remove_debuff" : True
        # }
        self.__type = config["type"]
        self.__flask_key = config["key"]
        self.__remove_ailment = config["remove_debuff"]

        # color method to read template. Must match color method used to grab the screenshot
        # self.__color_method = cv2.IMREAD_GRAYSCALE # grayscale doesn't work -> Same templates, different color
        if config["color_type"] == "color":
            self.__color_method = cv2.IMREAD_COLOR

        template_path = os.path.join("resources", "debuff_templates", f"{self.__type}.png")
        file_exists = os.path.exists(template_path)
        if not file_exists:
            raise customErrors.FileConfigError(template_path)

        self.__template_img = cv2.imread(template_path, self.__color_method)

        self.__keyboad = Controller()

        self.__last_used = dt.datetime.now()- dt.timedelta(seconds=10) # will be changed after each effect removal
        self.last_action = {}  # will be changed after each run( call

    def run(self, current_screen):
        """
        Causes the the effect check to run and removes effect if it exists

        :param current_screen: partial screenshot of upper left area
        :type current_screen: np.array

        :return: empty dict if no action, action_dict if debuff was removed
        :rtype: dict
        """

        timedelta_seconds = (dt.datetime.now()-self.__last_used).seconds
        if timedelta_seconds < 4:
            info = f"{self.__type}: Immunity lock still active (4s total)"
            logger.info(info)
            self.last_action = {}
            return {}

        effect_exists = self.check_ailment(current_screen)

        if not effect_exists:
            return {}

        if effect_exists:
            self.perform_action()
            dt_pressed = dt.datetime.now()

        action_dict = {"type": str(self.__type), "key_pressed": str(self.__flask_key)}
        self.last_action = action_dict
        logger.info(action_dict)
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

        if show_match:
            height, width, d = self.__template_img.shape
            top_left = max_loc
            bottom_right = (top_left[0] + width, top_left[1] + height)
            cv2.rectangle(current_screen, top_left, bottom_right, (0, 0, 255), 4)
            print(f"min_val: {min_val}, max_val: {max_val},\
            min_loc :{min_loc}, max_loc: {max_loc}")
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
        self.__last_used = dt.datetime.now()
        return True


# just for seperate manual tests. This won't be executed, when imported externally
# will be removed once Tool is completed
if __name__ == "__main__":
    resource_dir = os.path.join(os.getcwd(), os.pardir, "resources")
    example_dir = os.path.join(resource_dir, "example_pictures")
    example_img_path = os.path.join(example_dir, "ailments", "shock", "3.png")

    # read_color_method = cv2.IMREAD_GRAYSCALE
    read_color_method = cv2.IMREAD_COLOR
    # template_img = cv2.imread(template_img_path, read_color_method)
    example_img = cv2.imread(example_img_path, read_color_method)

    config = \
        {
            "type": "bleed",
            "key": "1",
            "color_type": "color",
            "remove_debuff": True
        }
    status_chill = Status(config)
    result = status_chill.check_ailment(example_img, show_match=True)
    print(result)
