import os
import re
import sys
import json
import numpy as np
import concurrent.futures # running multiple extractions at once

from time import perf_counter
from statistics import median
from operator import itemgetter

# local packages
from LammpsPackage.bed_analysis import RegFile, DiscFile
import var

# importing task variables
TASK_ID = var.TASK_ID
TRIAL_ID = var.TRIAL_ID

TEST_FLAG = sys.argv

def get_points(
    time: tuple[int, int],
    bed_obj: RegFile, 
    pIDs: list[int], 
    disc_params: tuple[float, float, float]
    ) -> tuple[tuple[float, float], tuple[float, float], list[int]]:
    """
    Function to get the coordinate points for the mound and the crater
        - Args
            - `time` : the index, timestep tuple to specify the timestep
            - `bed_obj` : the dmp.reg file read in as an object
            - `pIDs` : the particle ID's to look at
            - `disc_params` : the (x, y, r) parameters of the disc passed in for contact
        - Returns
            - `bed.crater` : coordinate points of the crater in the bed
            - `(mound_x, mound_y)` : coordinate points of the mound on the bed
            - `touch_idx` : the IDs of the particles that the disc touches at that timeframe
    """
    
    #* computing the reduced bed
    bed = bed_obj.get_bed(*time, pIDs) # method returns a _Bed object

    #* bed.surface
    #* bed.crater

    #* computing the mound of the bed
    dataDict = bed.get_input()

    #! performance counter
    start_mound = perf_counter()

    # computing the particle density from the
    RADIUS_MULTIPLIER = 4
    for key in dataDict:
        dataDict[key]['p_count'] = bed.profile.P_count_near_particle( dataDict[key]['x'], dataDict[key]['y'], RADIUS_MULTIPLIER )
    
    # sorting the particles with more than 6 near counts by height
    possible_mound = sorted(
        [
            [ dataDict[key]['x'],dataDict[key]['y'] ] for key in dataDict if (dataDict[key]['p_count'] > 6) and (dataDict[key]['x'] > bed.crater[0])
        ],
        key = itemgetter(1)
    )

    # finding the x coordinate of the particle that has the smallest position with the computed mound height
    xs = [pick[0] for pick in possible_mound[-9:]]
    ys = [pick[1] for pick in possible_mound[-9:]]
    
    mound_y = median(ys)
    mound_x = xs[
        min( range(len(xs)) ,
        key = lambda i: abs(xs[i] - mound_y) ) #! What's happening here???
    ]
    end_mound = perf_counter()
    print(f"  (mound time: {end_mound-start_mound: .3f})")

    # determining contact points
    disc_x, disc_y, disc_r = disc_params

    #* disc_r * (the ratio of the disc R to the single particle R + disc R) * 110%
    touch_idx = bed.is_within_circle( (disc_x, disc_y), disc_r*((1197+8075)/8075)*1.1)

    return bed.crater, (mound_x, mound_y), touch_idx

def get_data_dict(bed_filepath: str, disc_filepath: str) -> dict:
    """
    Function to unpack the data from the input files into a single dictionary with arrays
        - Args
            - `bed_filepath` : the `dmp.reg` file to examine
            - `disc_filepath` : the `dmp.disc` file to examine 
            - 
    """
    pBed = RegFile(bed_filepath)
    pDisc = DiscFile(disc_filepath)

    initBed = pBed.get_init_bed()
    
    # setting in the output dictionary to the parameters in the disc 
    outDict = {key: pDisc.get_data(key, as_array=True) for key in pDisc.dataDict[pDisc.timestep0]}

    #! resize the bed to minimize the looping times
    #! 1.4 --> 2.5 seconds
    #! 1.35 --> 3.0 seconds
    reduced_idx = initBed.is_greater('y', 0.14)

    #* the timesteps for which the data is significant
    # ts_cutoff = pDisc.ts_cutoff
    # reduced_ts = [ (t,b) for t,b in pBed.ts if b <= pDisc.ts_cutoff ]
    reduced_ts = [ (t,b) for t,b in pBed.ts if b in pDisc.ts ]

    # initializing the arrays
    outDict['crater_xs'] = list(np.zeros(len(reduced_ts), dtype=float))
    outDict['crater_ys'] = list(np.zeros(len(reduced_ts), dtype=float))
    outDict['mound_xs'] = list(np.zeros(len(reduced_ts), dtype=float))
    outDict['mound_ys'] = list(np.zeros(len(reduced_ts), dtype=float))
    
    #* a set that contains the pIDs of the particles that encounter the disc
    particles_touched = set()

    #todo   Add a breaking condition here. This should be something that is retrieved from the disc file
    for idx,time in enumerate(reduced_ts):
        print(f"Iteration {bed_filepath[-8:]}\tTimestep: {time[1]}", end = "")

        (outDict['crater_xs'][idx], outDict['crater_ys'][idx]), (outDict['mound_xs'][idx], outDict['mound_ys'][idx]), touch_IDs = get_points(
            # args for get_points()

            time, 
            pBed, 
            reduced_idx,
            (
            #* recall that for the disc, it's not called by the timestep
            #* as they are all loaded as arrays already
                outDict['disc_xs'][idx],
                outDict['disc_ys'][idx],
                outDict['disc_rs'][idx]
            )
        )
        # updating the list with the unique particles encountered by the disc
        particles_touched.update(touch_IDs)

        # printing the status
        print(
            f"\
                \r\tcrater_x: {outDict['crater_xs'][idx]}\n \
                \r\tcrater_y: {outDict['crater_ys'][idx]}\n \
                \r\tmound_x: {outDict['mound_xs'][idx]}\n \
                \r\tmound_y: {outDict['mound_ys'][idx]}\n \
                \r\tcontact_pIDs: {len(particles_touched)}\n"
        )
    
    outDict['contact_pIDs'] = list(particles_touched)
    outDict["box_width"] = pBed.box_width
    outDict["box_height"] = pBed.box_height

    return outDict

def get_disc_paths(filepath: str):
    """
    Function to get the path of the disc (and relevant data)
    #! Not in use as of "testing5" --> functionality combined into the get_points() function
    """
    start = perf_counter()

    disc = DiscFile(filepath)

    end = perf_counter()
    # print(f"Accessed disc data for {re.findall('V[0-9]+\.?[0-9]+_A[0-9]+',filepath)[0]} in {end-start: .2f} seconds")
    
    # getting the arrays from the keys from the first timestep
    return {key: disc.get_data(key, as_array=True) for key in disc.dataDict[disc.timestep0]}

def get_path(filetype: str, angle: str) -> list[str]:
    """
    Function to get the filepaths for the angles
    """

    # base = Path(os.getcwd()).parent.absolute() #* getting the parent directory

    all_files = os.listdir( var.raw_root )

    if filetype == "bed":
        return [ f"{var.raw_root}/{i}" for i in all_files if all( [ (j in i) for j in [var.TASK_ID,"dmp.reg",str(angle)] ] ) ]
    elif filetype == "disc":
        return [ f"{var.raw_root}/{i}" for i in all_files if all( [ (j in i) for j in [var.TASK_ID,"dmp.disc",str(angle)] ] ) ]

    else:
        raise Exception(f"The input parameter \"{filetype}\" is invalid")


def extract_to_json(bed_filepath: str, disc_filepath: str):

    outDict = get_data_dict(bed_filepath, disc_filepath)

    #todo   Write in values for keys ['num_timesteps'] and ['disc_r'] maybe for compatibility at the end of dict

    iteration = re.findall('V[0-9]+\.?[0-9]+_A[0-9]+',bed_filepath)[0]
    os.makedirs(f"{var.extract_root}/data_Extract_{var.TASK_ID}_{var.TRIAL_ID}", exist_ok=True)
    with open(f"{var.extract_root}/data_Extract_{var.TASK_ID}_{var.TRIAL_ID}/outputs_{iteration}.json", 'w') as file:
        json.dump(outDict, file, indent=4)

def extract_to_json_test(bed_filepath: str, disc_filepath:str)-> None:
    outDict = get_data_dict( bed_filepath,disc_filepath )

    dest_dir = f"{var.extract_root}/data_Extract_TEST_{var.TASK_ID}_{var.TRIAL_ID}"
    os.makedirs(dest_dir, exist_ok=True)

    # saving the data
    iteration = re.findall('V[0-9]+\.?[0-9]+_A[0-9]+',bed_filepath)[0]
    with open(f"{dest_dir}/outputs_{iteration}.json", 'w') as file:
        json.dump(outDict, file, indent=4)

    print(
        f"Test file \"{dest_dir}/outputs_{iteration}.json\" successfully written!"
    )


def main():
    #* loop over angles and such here 
    
    if "-test" not in TEST_FLAG:
        for angle in var.angles:
            beds = []
            discs = []
            # for velocity in [f"{vel:6.4f}" for vel in velocities]:
            beds =  get_path("bed", f"_A{angle}") 
            discs = get_path("disc", f"_A{angle}")

            # debug print
            # for idx,(bed,disc) in enumerate(zip(beds,discs)):
            #     print(f"{idx:2d} -> {bed} | {disc}")
            # print("")

            # using multiple processors
            with concurrent.futures.ProcessPoolExecutor() as executor:
                executor.map(extract_to_json, beds, discs)

    # testing for single v and a happens if test flag exists
    else: 
        angle = TEST_FLAG[TEST_FLAG.index("-test")+1]
        velocity = TEST_FLAG[TEST_FLAG.index("-test")+2]

        bed = [b for b in get_path("bed", f"_A{angle}") if str(velocity) in b]
        disc = [d for d in get_path("disc", f"_A{angle}") if str(velocity) in d]

        extract_to_json_test( bed[0],disc[0] )


if __name__ == "__main__":
    
    start = perf_counter()
    main()
    end = perf_counter()

    print(f"Total runtime: { int( (end-start)//60 ) }:{(end-start)%60 : .2f}")
    with open("logfile.txt", 'w') as logfile:
        logfile.write(f"Total runtime: { int( (end-start)//60 ) }:{(end-start)%60 : .2f}")
    
