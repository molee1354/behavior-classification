#!/bin/bash
for FILE in *; do
    if [[ "$FILE" == *".sbatch"* ]]
    then
        sbatch $FILE
    fi
done
    
