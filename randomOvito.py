import json
from time import sleep
import numpy as np
import pyautogui as pg
import sys
from random import shuffle

sleep(5)
#* C:\Users\moosu\projects\Research\lammps_LIS01\Output\lmpDump_LIS01\lmpDump_A20\iteration_V1.0_A20\dmp.reg.LIS01_V1.0_A20
class Filepaths:

    def __init__(self,task:str, angle: int, vel: float) -> None:
        self.path_name = f"C:\\Users\\moosu\\projects\\Research\\lammps_LIS01\\Output\\lmpDump_{task}\\lmpDump_A{angle}\\iteration_V{vel}_A{angle}\\dmp.reg.{task}_V{vel}_A{angle}"

        # print(self.path_name)
    
    @staticmethod
    def do_process( pathName):
        sleep(1.5)
        # pg.hotkey('alt','tab') #switching back to ovito
        pg.hotkey('ctrl','i')
        pg.write(pathName)
        pg.press('enter')
        pg.press('enter')

try:
    task = sys.argv[1]
except IndexError:
    task = "LIS01"
    
velocities = np.linspace(1.0, 7.0, 13)
angles = np.linspace(20, 70, 11, dtype=int)

pathNames = []
for angle in angles:
    for velocity in velocities:
        path = Filepaths(task, angle, velocity)

        pathNames.append(path.path_name)

shuffle(pathNames)

inputBehavior = {}
for idx, element in enumerate(pathNames):
    Filepaths.do_process(element)
    inputBehavior[element[-8:]] = input(f"[{idx}] Input behavior: ")

    with open(f"Human_Behavior_{task}.json", 'w') as jsonOut:
        json.dump(inputBehavior,jsonOut, indent=4)

    pg.hotkey('alt', 'tab')
