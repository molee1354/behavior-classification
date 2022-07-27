# variables needed for operation
import numpy as np

# where the necessary data is stored
extract_root = "E:/mokin/behavior_classification/data_Extracts"
raw_root = "E:/mokin/moon_raw"

# where the outputs should go
output_root = "E:/mokin/behavior_classification/outputs"

# task/trial id
TASK_ID = "Moon_1x"
TRIAL_ID = "extract_4"

angles = np.linspace(20, 70, 11, dtype=int)

# for writing .sbatch outputs
py_cmd = "python3 pathExtract_p.py"
parallel = 9
