import os
from debufftracker import screen_tools

current_dir = os.path.dirname( os.path.abspath(__file__))
project_dir = os.path.join(current_dir, os.path.pardir)

# set project source folder as working directory
os.chdir(project_dir)

if __name__ == "__main__":
    screentracker = screen_tools.ScreenTracker()
    screentracker.create_status_instances()
    screentracker.run()