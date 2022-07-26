from pathExtract import *
import sys

def main():
    # just a script to run the extract_to_json() function

    reg_file = sys.argv[1]
    disc_file = sys.argv[2]

    extract_to_json( reg_file,disc_file )


if __name__ == "__main__":
    main()


