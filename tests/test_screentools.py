from debufftracker import screen_tools as sct
import pytest
import os

current_dir = os.path.dirname( os.path.abspath(__file__))
project_dir = os.path.join(current_dir, os.path.pardir)

# set project source folder as working directory
os.chdir(project_dir)


def test_configreader():
    cr = sct.ConfigReader()
    image_config = cr.get_imagetransformation_config()
    keys = ["width", "height", "color_type"]
    for key in keys:
        assert key in image_config.keys(), f"{key} not in {image_config.keys()}"

    status_type = "ailment"
    debuff_config = cr.get_debuff_configs(status_type)
    keys = ["shock", "ignite", "bleed"]
    for key in keys:
        assert key in debuff_config.keys(), f"{key} not in {debuff_config.keys()}"


def test_screentracker_config():
    st = sct.ScreenTracker()
    st.create_status_instances()
    assert isinstance(st.status_instances, dict), "status.__status_instances is no dict"
    assert len(st.status_instances) >= 1, "status.__status_instances contains no key"


def test_screentracker_grabscreen():
    st = sct.ScreenTracker()
    st.create_status_instances()
    screen = st.grab_transform_screen() # height, width, channels
    img_config = st.image_config
    assert isinstance(img_config, dict), "ScreenTracker.img_config is not type dict"
    assert img_config["height"] == screen.shape[0]
    assert img_config["width"] == screen.shape[1]
