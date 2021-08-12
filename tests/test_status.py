from debufftracker import status
import pytest
import os
import cv2


def test_template_image_folder():
    template_folder = os.path.join(os.getcwd(), os.pardir, "resources", "debuff_templates")
    assert os.path.isdir(template_folder), "template_folder does not exist"


configs = \
[
    {
        "type" : "bleed",
        "key" : "1",
        "color_type" : "color",
        "remove_debuff" : True
    },
    {
        "type": "poison",
        "key": "2",
        "color_type": "color",
        "remove_debuff": True
    }
]


@pytest.mark.parametrize("config", configs)
def test_create_status_instances(config):
    status.Status(config)

configs = \
[
    {
        "type" : "bleed",
        "key" : "1",
        "color_type" : "color",
        "remove_debuff" : True
    },
    {
        "type": "poison",
        "key": "2",
        "color_type": "color",
        "remove_debuff": True
    },
    {
        "type": "bleed",
        "key": "1",
        "color_type": "color",
        "remove_debuff": True
    }
]

screen_bleed = os.path.join(os.getcwd(), os.pardir, "resources", "example_pictures", "ailments", "bleed", "1.png")
screen_poison = os.path.join(os.getcwd(), os.pardir, "resources", "example_pictures", "ailments", "poison", "2.png")
# this one might cause a false positive, if major changes occur
screen_shock = os.path.join(os.getcwd(), os.pardir, "resources", "example_pictures", "ailments", "shock", "3.png")

image_paths = [screen_bleed, screen_poison, screen_shock]
results = [True, True, False]

param_inputs = [(config, image_path, result) for (config, image_path, result) in zip(configs, image_paths, results)]


@pytest.mark.parametrize("config, img_path, result", param_inputs)
def test_status_check_ailment(config, img_path, result):
    print(config, img_path, result)
    img = cv2.imread(img_path, cv2.IMREAD_COLOR)
    st = status.Status(config)

    assert st.check_ailment(current_screen=img) == result


