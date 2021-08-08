import numpy as np
import datetime as dt
import mss
import toml
from debufftracker import errors as customErrors
from debufftracker import status
import time
import logging
import os
import json
from threading import Thread


class ConfigReader:
    """
    This class contains functions to read and return configuration Data
    """
    def __init__(self):
        self.__config_path = os.path.join(os.getcwd(), os.pardir, "resources", "config.toml")
        self.__toml_content = toml.load(f=self.__config_path)


    def get_imagetransformation_config(self):
        allowed_colors = ["color"]
        if self.__toml_content["imagetransformation"]["color_type"].lower() not in allowed_colors:
            raise customErrors.ColorConfigError(self.__toml_content["imagetransformation"]["color_type"])
        return self.__toml_content["imagetransformation"]


    def get_debuff_configs(self, status_type): # ailment/curse/ground
        status_config = self.__toml_content[status_type]
        return status_config


class ScreenTracker:
    """
    This class contains functions to track the screen content
    """
    def __init__(self):
        self._config_reader = ConfigReader()
        self.__image_config = self._config_reader.get_imagetransformation_config()

    def create_removestatus_dict(self):
        """
        Iterates over each status type in ["ailment", "curse", "ground"] and adds the status specific config
        to dictionary relevant_dicts. Then return relevant dict
        :return: relevant_dicts, a dictionary with status configs.
        :rtype: Dictionary
        """
        def get_relevant_dicts(d):
            """
            A helpfunction, only callable inside create_removestatus_dict, to "flatten" a dictionary and
            only return results where remove_debuff is True

            :param d: dictionary that contains sub dictionaries. Each subdictionary represents a status config
            :return: big_dict. Da Dictionary that only contains configs where subdict["remove_debuff"] == True)
            :rtype: Dictionary
            """
            big_dict = {}
            for key in d.keys():
                # "Flatten" dictionary if True
                if (d[key]["key"] !="") and (d[key]["remove_debuff"] == True):
                    big_dict[key] = d[key]
                elif (d[key]["key"] =="") and (d[key]["remove_debuff"] == True):
                    raise customErrors.StatusConfigError("if remove_debuff is true, then keybinding must be set")

            return big_dict

        relevant_dicts = {}
        status_types = ["ailment", "curse", "ground"]
        for status_type in status_types:
            status_type_all_dict = self._config_reader.get_debuff_configs(status_type=status_type)
            status_type_remove_dict = get_relevant_dicts(status_type_all_dict)
            relevant_dicts.update(status_type_remove_dict)

        self.__removestatus_dicts = relevant_dicts #dict contains dicts
        # dict structure
        # removestatus_dicts=\
        #     {
        #         "shocK":
        #             {
        #                 "type" : "shock",
        #             }
        #     }

        return relevant_dicts


    def create_status_instances(self):
        """
        Create instances of status.Staus and add them to a dictionary self.__status_instances.
        Using this dictionary enables managing those instances, when necessary

        :return: None
        """

        # config example needed to initiate status classes
        # config = \
        # {
        #     "type" : "bleed",
        #     "flask_key" : "1",
        #     "color_type" : "gray",
        #     "remove_debuff" : True
        # }

        try:
            remove_status_dicts = self.__removestatus_dicts
        except:
            remove_status_dicts = self.create_removestatus_dict()

        status_instances_dict = {}
        for status_type in remove_status_dicts.keys():
            #print(remove_status_dicts)
            status_config = remove_status_dicts[status_type]
            #add color_type to config. This is required to read the template with the correct method (gray/color)
            status_config["color_type"] = self.__image_config["color_type"]
            status_instance = status.Status(status_config)
            status_instances_dict[status_type] = status_instance

        self.__status_instances = status_instances_dict


    def manage_status_instances(self):
        """
        Takes a partial screenshot, then iterates over the status.Status instances and checks if a harmful effect of
        type of instance was found. If so, remove the effect. Threads will be joined to prevent chaotic behaviour.

        :return: debuffs_dict, a dict that contains the negative effect and a dt stamp when it was recognized
        :rtype: Dictionary
        """

        #https://www.geeksforgeeks.org/how-to-create-a-new-thread-in-python/
        screen = self.grab_transform_screen()
        debuffs_dict = {}
        thread_list = []
        for status_name in self.__status_instances.keys():
            status_instance = self.__status_instances[status_name]
            #status_instance.run(screen) # each instance is run as a seperate Thread
            t = Thread(target=status_instance.run, args=(screen, ))
            thread_list.append(t)
            t.start()
            #
            # debuff_status = status_instance.last_action
            # # if len(debuff_status) > 0:
            # #     debuff_status_str = json.dumps(debuff_status)
            # #     print(debuff_status)

        # wait for threads to finish. Not waiting caused chaotic behavior.
        for t in thread_list:
            t.join()

        return debuffs_dict


    def run(self):
        """
        Infinitive loop that calls self.get_debuffs() which causes any found negative effects to be removed.

        :return: None
        """
        continue_run = True
        print("Debuff Tracker started")
        while continue_run==True:
            self.manage_status_instances()
            # if len(debuffs) > 0:
            #     print(debuffs)
            time.sleep(1)

    def grab_transform_screen(self):
        """
        Make a partial Screenshot, transform to screenshot to numpy array and return transformed screenshot.

        :return: screen_cv2, partial screenshot that contains all 3 color channels. Order is BGR
        :rtype: np.array
        """

        # I compared 3 methods over 1000 iterations:
        # pyautogui: take screenshot, then cut and transform (avg time 0:00:00.054545)
        # PIL: take partial screenshot, then transform (avg time 0:00:00.035084)
        # mss: take partial screenshot, then transform (avg time 0:00:00.013324)
        # mss is lightweight and fast
        with mss.mss() as sct:
            # The screen part to capture
            monitor_area = \
                {
                    "top": 0,
                    "left": 0,
                    "width": self.__image_config["width"],
                    "height": self.__image_config["height"]
                }
            screen = sct.grab(monitor_area)
            screen_cv2 = np.array(screen)
            screen_cv2 = screen_cv2[:,:,:3] # 4th channel contains valu 255 (uint8). Remove fourth channel

            end_dt = dt.datetime.now()
            fname = str(end_dt).replace(":", "") + ".png"
            p = os.path.join(os.getcwd(), os.pardir, "resources", "track_screen", fname)
            #cv2.imwrite(p, screen_cv2)
            #
            # cv2.imshow('main.py', screen_cv2)
            # cv2.waitKey()

        return screen_cv2


if __name__ == "__main__":
    screentracker = ScreenTracker()
    screentracker.create_status_instances()
    screentracker.run()