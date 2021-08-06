import numpy as np
import cv2
import datetime as dt
import mss
import toml
from debufftracker import errors as customErrors
from debufftracker import status
import time

import os


class ConfigReader:

    def __init__(self):
        self.__config_path = os.path.join(os.getcwd(), os.pardir, "resources", "config.toml")
        self.__toml_content = toml.load(f=self.__config_path)


    def get_imagetransformation_config(self):
        allowed_colors = ["gray", "color"]
        if self.__toml_content["imagetransformation"]["color_type"].lower() not in allowed_colors:
            raise customErrors.ColorConfigError(self.__toml_content["imagetransformation"]["color_type"])
        return self.__toml_content["imagetransformation"]


    def get_debuff_configs(self, status_type): # ailment/curse/ground
        status_config = self.__toml_content[status_type]
        return status_config


class ScreenTracker:

    def __init__(self):
        self._config_reader = ConfigReader()
        self.__image_config = self._config_reader.get_imagetransformation_config()

    def create_removestatus_dict(self):
        def get_relevant_dicts(d):
            big_dict = {}
            for key in d.keys():
                if (d[key]["key"] !="") and (d[key]["remove_debuff"] == True):
                    big_dict.update(d)
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


    def get_debuffs(self):
        start_dt = dt.datetime.now()
        screen = self.grab_transform_screen()
        debuffs_dict = {}
        for status_name in self.__status_instances.keys():
            # print(status_name)
            status_instance = self.__status_instances[status_name]
            r = status_instance.check_ailment(screen)
            if r == True:
                debuffs_dict[status_name] = f"Found {dt.datetime.now()}"

        end_dt = dt.datetime.now()

        return debuffs_dict


    def run(self):
        continue_run = True
        while continue_run==True:
            debuffs = self.get_debuffs()
            if len(debuffs) > 0:
                print(debuffs)
            time.sleep(2)

    def grab_transform_screen(self):

        # I compared 3 methods over 1000 iterations:
        # pyautogui: take screenshot, then cut and transform (avg time 0:00:00.054545)
        # PIL: take partial screenshot, then transform (avg time 0:00:00.035084)
        # mss: take partial screenshot, then transform (avg time 0:00:00.013324)
        # mss is lightweight and fast
        with mss.mss() as sct:
            # The screen part to capture
            monitor_area = {"top": 0, "left": 0, "width": 500, "height": 250}
            screen = sct.grab(monitor_area)
            screen_cv2 = np.array(screen)

            end_dt = dt.datetime.now()
            fname = str(end_dt).replace(":", "") + ".png"
            p = os.path.join(os.getcwd(), os.pardir, "resources", "track_screen", fname)
            cv2.imwrite(p, screen_cv2)

            screen_cv2 = cv2.cvtColor(screen_cv2, cv2.COLOR_BGR2GRAY)
        return screen_cv2


if __name__ == "__main__":
    screentracker = ScreenTracker()
    screentracker.create_status_instances()
    screentracker.run()
    #screentracker.get_debuffs()
    #screentracker.grab_transform_screen()