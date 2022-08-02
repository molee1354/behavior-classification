import os
import sys
import json
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

import var

# importing variables
try:
    TASK_ID = sys.argv[1]
except IndexError:
    TASK_ID = var.TASK_ID

try:
    TRIAL_ID = sys.argv[2]
except IndexError:
    TRIAL_ID = var.TRIAL_ID


def processData(data_dict: dict) -> tuple[list[int],list[float]]:
    """
    Function to process the input dictionaries to a 2D list for plotting
        - Args
            - `data_dict`: dictionary of behaviors (and confidence)
        - Returns
        - 2-D array for the matshow plot
    """
    
    # for the normal dictionary 
    if type(next(iter(data_dict.values()))) == str: 
        # this way the data type of the computer output can be anything other than "str"
        behaviorsList = []
        confidenceList = []
        for angle in var.angles:
            behaviorList_I = []
            confidenceList_I = []
            # for velocity in np.linspace(1.0, 7.0, 13):
            for key in [k for k in data_dict.keys() if f"_A{angle}" in k]:

                # making a placeholder confidence list
                confidenceList_I.append(0.7)

                if data_dict[key] == "FS":
                    behaviorList_I.append(0)
                if data_dict[key] == "RO":
                    behaviorList_I.append(1)
                if data_dict[key] == "RC":
                    behaviorList_I.append(2)

            behaviorsList.append(behaviorList_I)
            confidenceList.append(confidenceList_I)

        return behaviorsList,confidenceList
    
    # extracting the confidence values 
    #todo the loaded data is now a key-value thing so the indexing should change
    # else:
    behaviorsList = []
    confidenceList = []
    for angle in var.angles:
        # initializing each row 
        behaviorList_I = []
        confidenceList_I = []
        for key in [k for k in data_dict.keys() if f"_A{angle}" in k]:

            # adding the confidence
            confidenceList_I.append(data_dict[key]["confidence"])

            if data_dict[key]["behavior"] == "FS":
                behaviorList_I.append(0)

            if data_dict[key]["behavior"] == "RO":
                behaviorList_I.append(1)
                
            if data_dict[key]["behavior"] == "RC":
                behaviorList_I.append(2)

        behaviorsList.append(behaviorList_I)
        confidenceList.append(confidenceList_I)

    return behaviorsList, confidenceList 
    


def main():

    behavior_savepath = f"{var.output_root}/behaviors/computer"
    with open(f"{behavior_savepath}/Computer_Behavior_{TASK_ID}_{TRIAL_ID}.json", 'r') as readC:
        compDict = json.load(readC)

    # the human dictionary is probably not sorted
    # try:
    with open(f"{var.output_root}/behaviors/human/Human_Behavior_{TASK_ID}.json", 'r') as file:
        humanDict = json.load(file)
    
    # if there is no json file to refer to, go to the old xlsx file
    # except FileNotFoundError:
    #     wb_file = pxl.load_workbook(f"behaviors/human/{TASK_ID}_batchManager.xlsx") #only need relative path
    #     sheet = wb_file.active
    #     MAXROW = sheet.max_row
    #     humanDict = {}
    #     for i in range(2, MAXROW+1):
    #         iterations_H = sheet.cell(row = i, column = 1).value
    #         behavior_H = sheet.cell(row = i, column = 4).value

    #         humanDict[iterations_H] = behavior_H
    
    #finding the unmatching keys
    # unmatching = []
    # for key in compDict:
    #     if compDict[key]['behavior'] != humanDict[key]:
    #         unmatching.append(key)

    #extracting x and y axes from the humanDict dictionary
    y_axis = list(np.linspace(20, 70, 11, dtype=int)) # angle
    x_axis = list(np.round(np.linspace(0.4064,2.8446,13),4))
    
    # total_iter = len(x_axis)*len(y_axis)

    #calling the function on the dictionaries
    # humanBehavior = np.array(processData(humanDict))
    comp_decision = processData(compDict)
    
    compBehavior = np.array(comp_decision[0])
    confidence = np.array(comp_decision[1])

    # diffBehavior = np.logical_xor(humanBehavior, compBehavior)
    # diffBehavior = humanBehavior != compBehavior

    fig, (
        ax1,ax2
            ) = plt.subplots(1,2, figsize=(13,6), sharey=False)
    fig.suptitle(f"{TASK_ID} Behavior Comparison", 
        fontweight = "bold",
        fontsize = 16,
    )

    #colormap parameters
    myColors = (
        (199/255,45/255,34/255,1.0), 
        (224/255,227/255,34/255,1.0), 
        (64/255,133/255,27/255,1.0)
    )
    colors = LinearSegmentedColormap.from_list('Custom', myColors, len(myColors))

    #colormap parameters for matching/unmatching
    myColorsBW = (
        (0.8,0.8,0.8,1), 
        (0,0,0,1)
    )
    # colorsBW = LinearSegmentedColormap.from_list('Custom', myColorsBW, len(myColorsBW))

    #plotting
    ax1.set_title("Computer plot")
    ax1 = sns.heatmap(
        ax = ax1,
        data = compBehavior,
        yticklabels=y_axis,
        linewidths=2,
        cmap=colors,
        vmax=2, vmin=0
    )
    ax1.invert_yaxis()
    ax1.set_xticklabels(x_axis, rotation=45)
    ax1.set_xlabel("Velocities")
    ax1.set_ylabel("Angles")
    ax1.margins(1)

    colorbar1 = ax1.collections[0].colorbar
    colorbar1.set_ticks([0.33,1.0,1.66])
    colorbar1.set_ticklabels(["FS","RO","RC"])

    ax2.set_title(f"Confidence (Avg = {np.average(confidence): .3f})")
    ax2 = sns.heatmap(
        ax = ax2,
        data = confidence,
        yticklabels=y_axis,
        linewidths=2,
        cmap="Reds",
        # vmax=2, vmin=0
    )
    ax2.invert_yaxis()
    ax2.set_xticklabels(x_axis, rotation=45)
    ax2.set_xlabel("Velocities")
    ax2.set_ylabel("Angles")

    colorbar4 = ax2.collections[0].colorbar
    colorbar4.set_ticks(np.linspace(0,1,11)) 

    # ax2.set_title("Human Plot")
    # ax2 = sns.heatmap(
    #     ax = ax2,
    #     data = humanBehavior,
    #     yticklabels=y_axis,
    #     linewidths=2,
    #     cmap=colors,
    #     vmax=2, vmin=0
    # )
    # ax2.invert_yaxis()
    # ax2.set_xticklabels(x_axis, rotation=45)
    # ax2.set_xlabel("Velocities")
    # ax2.set_ylabel("Angles")

    # colorbar2 = ax2.collections[0].colorbar
    # colorbar2.set_ticks([0.33,1.0,1.66])
    # colorbar2.set_ticklabels(["FS","RO","RC"])

    # ax3.set_title("Unmatching")
    # ax3 = sns.heatmap(
    #     ax = ax3,
    #     data = diffBehavior,
    #     yticklabels=y_axis,
    #     linewidths=2,
    #     cmap=colorsBW,
    #     # vmax=2, vmin=0
    # )
    # ax3.invert_yaxis()
    # ax3.set_xticklabels(x_axis, rotation=45)
    # ax3.set_xlabel("Velocities")
    # ax3.set_ylabel("Angles")

    # colorbar3 = ax3.collections[0].colorbar
    # colorbar3.set_ticks([0.25, 0.75])
    # colorbar3.set_ticklabels(["Matching", "Unmatching"])
    
    
    

    # outputText = f"Matching Rate: {(total_iter-len(unmatching))/total_iter:.3}\n{len(unmatching)} Unmatching parameters: {unmatching}"
    plt.subplots_adjust(
        top=0.88,
        bottom=0.21,
        left=0.13,
        right=0.9,
        hspace=0.31,
        wspace=0.2
    )
    # plt.gcf().text(0.1, 0.1, outputText, fontsize=12)

    plots_savepath = f"{var.output_root}/output_plots/behavior_comparisons"
    os.makedirs(plots_savepath, exist_ok=True)
    plt.savefig(f"{plots_savepath}/behaviorPlot_{TASK_ID}_{TRIAL_ID}.svg", format = "svg")

    plt.show()
    # output_plots\behavior_comparisons
    
        

if __name__ == "__main__":
    main()
