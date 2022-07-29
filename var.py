# variables needed for operation
import numpy as np

# where the necessary data is stored
extract_root = "/home/mlee80/projects/behavior-classification/data_Extracts"
raw_root = "/scratch/mlee80/lmp_dumps/moon_raw"

# where the outputs should go
output_root = "/home/mlee80/projects/behavior-classification/outputs"

# task/trial id
TASK_ID = "Moon_1x"
TRIAL_ID = "extract_3"

angles = np.linspace(20, 70, 11, dtype=int)

# for writing .sbatch outputs
py_cmd = "python3 pathExtract_p.py"
parallel = 9
