#!/bin/bash

# ==================================== YOUR PARAMETERS HERE =======================================
# Store current user's name and conda environment name
USERNAME="gleb"
ENV_NAME="torch"

# Setup project data
PROJECT_NAME="IEC-CV"
BASE_DIR="/home/$USERNAME/projects"

# Set directory for stdout
STDOUT_DIR="$BASE_DIR/iec_logs/console/"

# =================================== DO NOT CHANGE THIS PART =====================================
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
CONDA_PATH_PREFIX="/home/$USERNAME/miniconda3/condabin"
CONDA_PATH_PREFIX="/home/$USERNAME/miniconda3/envs/$ENV_NAME/bin:$CONDA_PATH_PREFIX"

# Set script abspath
PROJECT_DIR="$BASE_DIR/$PROJECT_NAME"
SCRIPT_ABSPATH="$PROJECT_DIR/main.py"

# Set the prefix to the actual PATH and PYTHONPATH variables.
PATH="$CONDA_PATH_PREFIX:$PATH"
PYTHONPATH="$PROJECT_DIR:$PYTHONPATH"

# Set abspath to output log file.
# Vary the path according to the current date in format YYYY-MM-DD.
STDOUT_FILENAME=$(date +"%Y-%m-%d")
STDOUT_EXT=".log"
STDOUT_ABSPATH="${STDOUT_DIR}${STDOUT_FILENAME}${STDOUT_EXT}"

# Now run the script using Python3 and abspath to script.
python3 $SCRIPT_ABSPATH > $STDOUT_ABSPATH
