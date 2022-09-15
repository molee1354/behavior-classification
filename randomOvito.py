import os
import json
from time import sleep
import numpy as np
import pyautogui as pg
import sys
from random import shuffle

sleep(5)
#* C:\Users\moosu\projects\Research\lammps_LIS01\Output\lmpDump_LIS01\lmpDump_A20\iteration_V1.0_A20\dmp.reg.LIS01_V1.0_A20
class Filepaths:

    # def __init__(self,task:str, angle: int, vel: float) -> None:
    #     # self.path_name = f"C:\\Users\\moosu\\projects\\Research\\lammps_LIS01\\Output\\lmpDump_{task}\\lmpDump_A{angle}\\iteration_V{vel}_A{angle}\\dmp.reg.{task}_V{vel}_A{angle}"
    #     self.path_name = f"/run/media/moosung/9C33-6BBD/Shared/Research/Granular/data/task_Bennu_1x"

    #     # print(self.path_name)
    def __init__( self,sim_root:str ) -> None:
        self.sim_root = sim_root
    
    @staticmethod
    def do_process( pathName ):
        sleep(1.5)
        # pg.hotkey('alt','tab') #switching back to ovito
        pg.hotkey('ctrl','i')
        pg.write(pathName)
        pg.press('enter')
        pg.press('enter')

sim_filepath = f"/run/media/moosung/9C33-6BBD/Shared/Research/Granular/data/task_Bennu_1x"

# try:
#     task = sys.argv[1]
# except IndexError:
#     task = "LIS01"

reg_files = [reg for reg in os.listdir(sim_filepath) if "dmp.reg" in reg]

path_names = []
for file in reg_files:
    path = Filepaths( file )
    path_names.append(path.sim_root)

# for angle in angles:
#     for velocity in velocities:
#         path = Filepaths(task, angle, velocity)

#         pathNames.append(path.path_name)

shuffle(path_names)

inputBehavior = {}
for idx, element in enumerate(path_names):
    Filepaths.do_process(element)
    inputBehavior[element[-8:]] = input(f"[{idx}] Input behavior: ")

    with open(f"Human_Behavior_{task}.json", 'w') as jsonOut:
        json.dump(inputBehavior,jsonOut, indent=4)

    pg.hotkey('alt', 'tab')
