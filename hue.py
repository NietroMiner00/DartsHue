from dotenv import load_dotenv
from python_hue_v2 import Hue
import os

if __name__ == "__main__":
    load_dotenv()

    hue = Hue(os.getenv("HUE_BRIDGE_IP"), os.getenv("HUE_USER_TOKEN"))

    lights = hue.lights

    for light in lights:
        print(f"{light.light_id}: {light.metadata}")
    print(hue.lights[2].color_xy)