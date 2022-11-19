import os
import csv
import var
import json
import random as r

class Source:
    
    # defining constants
    IDS = 0
    FEATURES = 1
    LABELS = 2

    def __init__( self, input_file:str, human_file:str ) -> None:
        with open( human_file,'r' ) as file:
            self.human_dict = json.load(file)

        with open( input_file,'r' ) as file:
            self.input_dict = json.load(file)

        # making the output directory if necessary
        self.path =  f"{var.output_root}/csv"
        os.makedirs( self.path,exist_ok=True )

        self.behavior_counts = self.__get_behavior_count()

    def __get_behavior_count( self ) -> list[int]:
        """
        Method to normalize behavior to reduce bias
            -> duplicates the scenarios that have lesser occurences than the 
                maximum output behavior.
        """
        
        behavior_counts = [0,0,0]
        for value in self.human_dict.values():
            if value == "FS":
                behavior_counts[0] += 1
            if value == "RO":
                behavior_counts[1] += 1
            if value == "RC":
                behavior_counts[2] += 1

        return behavior_counts
    
    def get_data_matrix( self ) -> list[ list[str] | list[list[float]] | list[list[int]] ]:
        classes = []
        for key,value in self.input_dict.items():
            ids = f"{var.TASK_ID}_{key}"
            features = [
                value["contact_pIDs"],
                # value["airborne"],

                1 if value["surpasses"] else 0,
                1 if value["crater_out"] else 0,

                value["crater_final_x"],
                value["mound_final_x"],

                value["disc_final_x"],
                value["disc_final_y"],
                value["disc_max_y"]
            ]
            labels = [
                1 if self.human_dict[key] == "FS" else 0,
                1 if self.human_dict[key] == "RO" else 0,
                1 if self.human_dict[key] == "RC" else 0
            ]
            classes.append(
                [
                    ids,
                    features,
                    labels
                ]
            )
        return classes

    def normalize_data( self ) -> list[ list[str] | list[list[float]] | list[list[int]] ]:
        """
        Method to normalize the output behaviors in the data to reduce bias.
        """
        
        data_matrix = self.get_data_matrix()

        fss = [ c for c in data_matrix if c[self.LABELS] == [1,0,0] ]
        ros = [ c for c in data_matrix if c[self.LABELS] == [0,1,0] ]
        rcs = [ c for c in data_matrix if c[self.LABELS] == [0,0,1] ]

        max_behavior = max(self.behavior_counts)

        # duplicating a random class until the lengths are even
        for behavior in [fss,ros,rcs]:
            cap = len(behavior)-1 #-> picked from original pool
            while len(behavior) < max_behavior:
                behavior.append( behavior[ r.randint(1,cap) ] )

        # unpacking gets rid of the order of things
        return [*fss,*ros,*rcs]
    
    def write_to_csv( self,data_matrix:list[ list[str] | list[list[float]] | list[list[int]] ] ) -> None:
        ids_file = f"{self.path}/ids.csv"
        features_file = f"{self.path}/features.csv"
        labels_file = f"{self.path}/labels.csv"
 
        with open( ids_file,'a' ) as file:
            file_writer = csv.writer( file,delimiter=',' )
            for item in data_matrix:
                file_writer.writerow( [item[self.IDS]] )

        with open( features_file,'a' ) as file:
            file_writer = csv.writer( file,delimiter=',' )
            for item in data_matrix:
                file_writer.writerow( item[self.FEATURES] )

        with open( labels_file,'a' ) as file:
            file_writer = csv.writer( file,delimiter=',' )
            for item in data_matrix:
                file_writer.writerow( item[self.LABELS] )


def main() -> None:
    
    # write into the var.py file. All file operations are `appends`
    filepath = f"{var.output_root}/behaviors/computer/"  \
            f"Computer_Behavior_{var.TASK_ID}_{var.TRIAL_ID}.json"
    human = f"{var.human_root}/Human_Behavior_{var.TASK_ID}.json"

    datas = Source( input_file=filepath,human_file = human )

    normalized_mat = datas.normalize_data()
    datas.write_to_csv( normalized_mat )


if __name__ == "__main__":
    main()

