import os
import re
import sys
import json
import logging
# import numpy as np
from time import perf_counter

from LammpsPackage.post_processing import Comparer, Visualizer
import var
#todo   Implement task ID and trial ID to differentiate between tasks and such

# importing variables
try:
    TASK_ID = sys.argv[1]
except IndexError:
    TASK_ID = var.TASK_ID

try:
    TRIAL_ID = sys.argv[2]
except IndexError:
    TRIAL_ID = var.TRIAL_ID

def main():
    # loading the json file with human decisions for comparison
    # with open(f"behaviors/human/Human_Behavior_{TASK_ID}.json", 'r') as file:
    #     humanDict = json.load(file)

    # try:
    #     with open(f"behaviors/human/Human_Behavior_{TASK_ID}.json", 'r') as file:
    #         humanDict = json.load(file)

    # except FileNotFoundError:
    #     wb_file = pxl.load_workbook(f"behaviors/human/{TASK_ID}_batchManager.xlsx") #only need relative path
    #     sheet = wb_file.active
    #     MAXROW = sheet.max_row
    #     humanDict = {}
    #     for i in range(2, MAXROW+1):
    #         iterations_H = sheet.cell(row = i, column = 1).value
    #         behavior_H = sheet.cell(row = i, column = 4).value

    #         humanDict[iterations_H] = behavior_H

    # dictionary to hold the computer behavior classifications
    # unmatching = []

    # vectors to loop angles -> velocities
    # velocities = np.round(np.linspace(0.4064,2.8446,13),4)
    # angles = np.linspace(20, 70, 11, dtype=int)
    # velocities = [7.0]
    # angles = [25]

    # initializing return 
    compDict = {}

    extractsPath =  f"{var.extract_root}/data_Extract_{TASK_ID}_{TRIAL_ID}"
    for angle in var.angles:
        for path in [ f"{extractsPath}/{p}" for p in os.listdir(extractsPath) if f"_A{angle}" in p ]:

            try:
                #* creating an output object that holds the necessary data
                output = Comparer( path )

                comp_dec = output.behavior_obj
                
                #* plotting the output behavior and saving the figure
                plotter = Visualizer(comp_dec)

                save_path = f"{var.output_root}/output_plots/path_plots/path_plots_{TASK_ID}_{TRIAL_ID}"
                os.makedirs(save_path, exist_ok=True)
                
                # plotting function
                plotter.path_plots(save_path, "svg")

                #* saving the computer behavior
                #todo Export <<output.behavior_obj.decision>> this here
                #! comp_dec is a tuple --> (behavior, confidence)
                compDict[ re.findall( "V[0-9]+\.?[0-9]+_A[0-9]*",path )[0] ] = {
                    "behavior" : comp_dec.behavior,
                    "confidence": comp_dec.confidence,
                    "contact_pIDs": comp_dec.contact_pIDs,
                    # "airborne": comp_dec.airborne,
                    "surpasses": comp_dec.surpasses,
                    "crater_out": comp_dec.crater_out,

                    #TODO normalizing this can also be an option
                    "crater_final_x": comp_dec.crater_final, # final disc x position with respect to the final crater position
                    "crater_min_y": comp_dec.crater_min_y,
                    "mound_final_x": comp_dec.mound_final, # final disc x position with respect to the final mound position
                    "disc_final_x": comp_dec.disc_final_x,
                    "disc_final_y": comp_dec.disc_final_y, # final disc height
                    "disc_max_y": comp_dec.disc_max_y
                }

                
                #* printing the behavior output
                # if human_dec == comp_dec["behavior"]:
                #     behavior_str = f"Computer / Human: [{ comp_dec['behavior'] }/{human_dec}]\tConfidence: [{comp_dec['confidence']}]"
                # else:
                #     # behavior_str = f"Computer / Human: [{comp_dec[0]}/{human_dec}]\tConfidence: [{comp_dec[1]}] <-- UNMATCHING" 
                #     behavior_str = f"Computer / Human: [{ comp_dec['behavior'] }/{human_dec}]\tConfidence: [{comp_dec['confidence']}] <-- UNMATCHING" 
                #     unmatching.append(f"V{velocity}_A{angle}") 

                behavior_str = f"Behavior : [{ comp_dec.behavior }]\tConfidence: [{comp_dec.confidence}]"

                logs_savepath = f"{var.output_root}/output_logs"
                logs_savefile = f"{logs_savepath}/extract_{TASK_ID}_{TRIAL_ID}.log"
                if os.path.exists(logs_savefile):
                    os.remove(logs_savefile)

                os.makedirs(logs_savepath, exist_ok=True)
                logging.basicConfig( 
                    level = logging.INFO, 
                    format = "  %(message)s", 

                    # outputting to both a log file and the stdout 
                    handlers = [logging.FileHandler(logs_savefile), logging.StreamHandler(sys.stdout)]
                ) 
                logging.info(f"\n Iteration: {comp_dec.iteration}\t{behavior_str}") 
                # printing the reasons line by line 
                for idx, reason in enumerate(output.behavior_obj.reasons): 
                    logging.info(f"\tReason {idx}: {reason}") 

                # outputting the final vote 
                logging.info(f"\tVotes: {output.behavior_obj.decisionDict}")

            except ValueError:
                print(f"ValueError occured in {path}")
                pass

                

    # saving the computer behavior classifications    
    behavior_savepath = f"{var.output_root}/behaviors/computer"
    os.makedirs(behavior_savepath, exist_ok=True)
    with open(f"{behavior_savepath}/Computer_Behavior_{TASK_ID}_{TRIAL_ID}.json",'w') as file:        
        json.dump(compDict, file, indent=4)
        
if __name__ == "__main__":    
    start = perf_counter()    
    main()    
    end = perf_counter()    

    # showing the behavior plot
    # import behaviorPlots
    # behaviorPlots.main()

    print(f"Total runtime: { int( (end-start)//60 ) }:{(end-start)%60 : .2f}")
