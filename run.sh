#!/bin/bash

# In order to start and run this script automatically,
# You have to edit your PATH variable, so that
# it will be equal to the one after "conda activate env_name".
# In this example env_name="torch", but you are free to use any other name.

# Store path to conda environment binaries.
# You can get them by the following:
# 	conda activate env_name
#	echo $PATH
# It will return full contents of PATH. You can copy either it's full version,
# or only a part, that contains conda. It's totally up to you.
CONDA_PATH_PREFIX="/home/gleb/miniconda3/envs/torch/bin:/home/gleb/miniconda3/condabin"

# Set the prefix to the actual PATH variable
PATH="$CONDA_PATH_PREFIX:$PATH"

# Set abspath to script
SCRIPT_ABSPATH="/home/gleb/projects/IEC-CV/main.py"

# Now run the script using Python3 and abspath to script
python3 $SCRIPT_ABSPATH