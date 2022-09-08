import re
import json
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import var

class Classification:

    def __init__( self,filepath:str ) -> None:

        with open( filepath,'r' ) as f:
            self.data_dict = json.load(f)
            
        self.velocities, self.angles = self.__get_fields()

        # sorting the angles and velocities
        self.velocities.sort()
        self.angles.sort()

    def __get_fields( self ) -> tuple[list,list]:
        """
        Function to get the velocity/angle fields in the human classification
        """

        velocities = set()
        angles = set()

        for key in self.data_dict: 
            velocities.add( re.findall("V([0-9]+\.[0-9]+)", key)[0] )
            angles.add( re.findall("_A([0-9]+)",key)[0] )

        return list(velocities),list(angles)


    def process_data( self ) -> None:
        """
        Function to convert the input human behavior dictionary into a plottable matrix
        """
        conversion = {
            "FS" : 0,
            "RO" : 1,
            "RC" : 2
        }

        behavior_matrix = []
        for angle in self.angles:
            behavior_array = []
            for velocity in self.velocities:
                try:
                    behavior = self.data_dict[f'V{velocity}_A{angle}']
                    behavior_array.append(conversion[behavior])
                except KeyError: # if the specific key does not exist
                    behavior_array.append(3)
                
            behavior_matrix.append(behavior_array)
        
        # set the behavior_matrix attribute
        self.behavior_matrix = behavior_matrix


    def plot_behavior_map( self ) -> None:
        """
        Function to plot the behavior map of the given data"""

        fig, ax = plt.subplots( 1,1, figsize=(5,5) )
        fig.suptitle( "Bennu Human Classification",
            fontweight="bold",
            fontsize=16
        )

        # colormap colors
        behavior_colors = (
            (199/255,45/255,34/255,1.0), 
            (224/255,227/255,34/255,1.0), 
            (64/255,133/255,27/255,1.0),
            (127/255,138/255,130/255,1.0)
        )
        colors = LinearSegmentedColormap.from_list(
            'Custom',
            behavior_colors,
            len(behavior_colors)
        )

        ax.set_title("Human Classification")
        ax = sns.heatmap(
            ax = ax,
            data = self.behavior_matrix,
            yticklabels = self.angles,
            linewidths = 2,
            cmap = colors,
            vmax = 3, vmin = 0
        )
        ax.invert_yaxis()
        ax.set_xticklabels( self.velocities,rotation=45 )
        ax.set_xlabel("Velocities (m/s)")
        ax.set_ylabel("Angles (deg)")
        ax.margins(1)

        colorbar = ax.collections[0].colorbar
        colorbar.set_ticks( [3*(1/8),3*(3/8),3*(5/8),3*(7/8)] )
        colorbar.set_ticklabels( ["FS","RO","RC","undef"] )

        # plot saving can be done here
        plt.subplots_adjust(
            top=0.88,
            bottom=0.2,
            left=0.13,
            right=0.95,
            hspace=0.2,
            wspace=0.2
        )
        plt.show()


def main() -> None:
    filepath = var.human_root
    # human_classification = Classification( f"{filepath}/Human_Behavior_Bennu_1x.json" )
    human_classification = Classification( f"{filepath}/Human_Behavior_Moon_1x.json" )
    human_classification.process_data()
    human_classification.plot_behavior_map()


if __name__ == "__main__":
    main()
