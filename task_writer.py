from pathExtract import *
import var

def main():

    # making the files list
    beds_list,discs_list = [],[]
    commands = { key:"" for key in range(var.parallel) }
    for angle in var.angles: 
        
        beds_list = get_path("bed", f"_A{angle}")
        discs_list =get_path("disc", f"_A{angle}")

        # storing the command
        for idx,(bed,disc) in enumerate(zip( beds_list,discs_list )):
            commands[ int(idx%var.parallel) ] += f"{var.py_cmd} {bed} {disc} && "
            
    # writing the .sbatch files
    for key in commands:     
        # removing the extra &&
        if commands[key][-3:-1] == "&&":
            commands[key] = commands[key][:-3]

        with open(f"extract_{key+1}.sbatch", 'w') as file:
            file.writelines( [
                "#!/bin/bash\n",
                f"#SBATCH -o extract_{key+1}.log\n",
                "#SBATCH -p standard\n",
                "#SBATCH -t 20:00:00\n",
                f"#SBATCH -n {var.parallel}\n",
                "#SBATCH --mem-per-cpu=200M\n",
                "echo Running on $SLURM_JOB_NODELIST\n",
                "module load python3/3.10.5b\n",
                "unset SLURM_GTIDS\n",
            ] )
            file.writelines(commands[key])
        print(f"Successfully created extract_{key+1}.sbatch!")


if __name__ == "__main__":
    main()
