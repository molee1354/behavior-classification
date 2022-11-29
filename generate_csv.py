import re
import os
import csv
import json
import random as r
from itertools import chain

import var


class Source:
    # index for output files
    IDS = 0
    FEATURES = 1
    LABELS = 2

    def __init__(self, all_data: list[str], all_human: list[str]) -> None:
        """
        all_data --> all the computer classifications from the simulation so
            that the data can be accessed

        all_human --> human classifications from one single human, independent
            of gravity environment
        """

        # extracting data from multiple files into a single dictionary 
        self.human_dict = self.__get_data_as_dict(all_human)
        self.input_dict = self.__get_data_as_dict(all_data)

        # making the output directory if necessary
        self.out_path = f"{var.output_root}/csv"
        os.makedirs(self.out_path, exist_ok=True)

    def __get_data_as_dict(self,json_list: list[str]) -> dict:
        """
        Method to combine the list of json files into a single dictionary
        that avoids key collision
        """
        out = {}
        for data_file in json_list:
            filekey = re.findall("[EMB][1234]", data_file)[0]

            try:
                with open(data_file, 'r') as file:
                    in_dict = json.load(file)
                    for k, v in in_dict.items():
                        out[f'{filekey}_{k}'] = v
            except FileNotFoundError:
                print(f"\"{data_file}\" not found!")
                pass


        return out

    def __get_behavior_count(self) -> list:
        """
        Method to get the counts for each behavior
        """
        behavior_counts = [0, 0, 0]
        for behavior in self.human_dict.values():
            if behavior == "FS":
                behavior_counts[0] +=1 
            if behavior == "RO":
                behavior_counts[1] +=1 
            if behavior == "RC":
                behavior_counts[2] +=1 

        return behavior_counts

    def get_data_matrix(self) -> list:
        """
        Method to collect the ids, features, and labels from the dictionaries
        """
        classes = []

        for key, value in self.input_dict.items():
            ids = key
            features = [
                value["contact_pIDs"],

                1 if value["surpasses"] else 0,
                1 if value["crater_out"] else 0,

                value["crater_final_x"],
                value["mound_final_x"],

                value["disc_final_x"],
                value["disc_final_y"],
                value["disc_max_y"]
            ]

            # the labels are collected from human classifications
            labels = [
                1 if self.human_dict[key] == "FS" else 0,
                1 if self.human_dict[key] == "RO" else 0,
                1 if self.human_dict[key] == "RC" else 0
            ]
            classes.append([
                ids, features, labels
            ])

        return classes

    def normalize_data(self) -> list:
        """
        Method to normalize the behaviors in the data.
        --> picking out the behavior with the least occurences, and
            randomly deleting other behavior points until the numbers match
        """

        data_matrix = self.get_data_matrix()

        fss = [ point for point in data_matrix if point[self.LABELS] == [1, 0, 0] ]
        ros = [ point for point in data_matrix if point[self.LABELS] == [0, 1, 0] ]
        rcs = [ point for point in data_matrix if point[self.LABELS] == [0, 0, 1] ]

        min_behavior_count = min(self.__get_behavior_count())
        for behavior in [fss, ros, rcs]:
            while len(behavior) > min_behavior_count:
                behavior.remove( behavior[ r.randint(0,len(behavior)-1) ] )

        return [*fss, *ros, *rcs]

    def write_to_csv(self, data_matrix: list[list]) -> None:
        """
        Method to write the collected data out into a csv file
        """

        ids_file = f"{self.out_path}/ids.csv"
        features_file = f"{self.out_path}/features.csv"
        labels_file = f"{self.out_path}/labels.csv"

        with open(ids_file, 'w') as file:
            file_writer = csv.writer(file, delimiter=',')
            for item in data_matrix:
                file_writer.writerow( [item[self.IDS]] )

        with open(features_file, 'w') as file:
            file_writer = csv.writer(file, delimiter=',')
            for item in data_matrix:
                file_writer.writerow( item[self.FEATURES] )

        with open(labels_file, 'w') as file:
            file_writer = csv.writer(file, delimiter=',')
            for item in data_matrix:
                file_writer.writerow( item[self.LABELS] )


def main() -> None:
    tasks = {
        "Earth_1x_cls1108" : ["E1", "E2"],
        "Moon_1x_cls1108" : ["M1", "M2", "M3", "M4"],
        "Bennu_1x_cls1108" : ["B1", "B2", "B3", "B4"]
    }
    names = [
        # "Ethan",
        "Mokin"
        # "Peter"
        ]

    all_data = [
        f"{var.output_root}/behaviors/computer/" \
        f"Computer_Behavior_{task}_{task_label}.json"
        for task, task_labels in tasks.items()
        for task_label in task_labels
    ]
    all_human = [
        f"{var.human_root}/{task_label}-{name}.json"
        for name in names
        for task_label in list( chain.from_iterable(tasks.values()) )
    ]

    # generating csv files
    datas = Source( all_data = all_data, all_human = all_human )
    normalized_mat = datas.normalize_data()
    datas.write_to_csv( normalized_mat )


if __name__ == "__main__":
    main()
