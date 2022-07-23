# variables needed for operation
import numpy as np

# where the necessary data is stored
extract_root = "/run/media/moosung/77FF-A557/data/data_Extracts"
raw_root = "/run/media/moosung/77FF-A557/data/moon_raw"

# where the outputs should go
output_root = "/run/media/moosung/77FF-A557/outputs"

# task/trial id
TASK_ID = "Moon_1x"
TRIAL_ID = "extract_3"

angles = np.linspace(20, 70, 11, dtype=int)


