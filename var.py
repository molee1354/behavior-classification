# variables needed for operation
import numpy as np

# where the necessary data is stored
extract_root = "/run/media/moosung/9C33-6BBD/Shared/Research/Granular/Code/Output_Refactor/data_Extracts"

raw_root = "/run/media/moosung/9C33-6BBD/Shared/Research/Granular/data/lmp_dumps/lmpDump_LIS02"

# where the outputs should go
output_root = "/home/moosung/projects/Research/Granular/behavior-classification/outputs"


# task/trial id
TASK_ID = "LIS02"
TRIAL_ID = "testing7"

angles = np.linspace(20, 70, 11, dtype=int)

# for writing .sbatch outputs
py_cmd = "python3 pathExtract_p.py"
parallel = 9
