import os
import var
import json
import csv


class Source:
    def __init__( self,input_file ) -> None:
        with open( input_file,'r' ) as file:
            self.input_dict = json.load(file)

        # making the output directory if necessary
        self.path =  f"{var.output_root}/csv"
        os.makedirs( self.path,exist_ok=True )


    def create_ids( self ) -> None:

        output_file = f"{self.path}/ids.csv"
        with open( output_file,'a' ) as file:
            file_writer = csv.writer( file,delimiter=',' )

            for key in self.input_dict:
                file_writer.writerow([f"{var.TASK_ID}_{key}"])


    def create_features( self ) -> None:
        
        output_file = f"{self.path}/features.csv"
        with open( output_file,'a' ) as file:
            file_writer = csv.writer( file,delimiter=',' )

            for value in self.input_dict.values():

                # writing out data as an array in each row
                #TODO -> perhaps add normalization?
                file_writer.writerow([
                    value["contact_pIDs"],
                    value["airborne"],

                    1 if value["surpasses"] else 0,
                    1 if value["crater_out"] else 0,

                    value["crater_final_x"],
                    value["mound_final_x"],

                    value["disc_final_x"],
                    value["disc_final_y"],
                    value["disc_max_y"]
                ])


    def create_labels( self ) -> None:
        """
        Method to write the `labels.csv` file by converting the \
                behavior into a 1x3 vector
        """

        output_file = f"{self.path}/labels.csv"
        with open( output_file,'a' ) as file:
            file_writer = csv.writer( file,delimiter=',' )
            
            behavior_index = {
                "FS" : [1,0,0],
                "RO" : [0,1,0],
                "RC" : [0,0,1]
            }

            for value in self.input_dict.values():
                file_writer.writerow([
                    behavior_index[value["behavior"]]
                ])


# converting the output behavior .json to .csv
def main() -> None:
    
    filepath = f"{var.output_root}/behaviors/computer/"  \
            f"Computer_Behavior_{var.TASK_ID}_{var.TRIAL_ID}.json"

    source = Source(filepath)
    source.create_ids()
    source.create_features()
    source.create_labels()


if __name__ == "__main__":
    main()
