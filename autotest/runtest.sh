# !/bin/bash

# Check if the current working directory is 'preswald'
if [[ $(basename "$PWD") != "preswald" ]]; then
    echo "Error: Script must be run from the 'preswald' directory."
    exit 1
fi

# Check if the example argument is provided
if [[ -z $1 ]]; then
    echo "Error: No test provided."
    exit 1
fi

# Reset frontend and preswald, then launch
example=$1
pip uninstall preswald
rm -rf dist/ build/ *.egg-info
python setup.py build_frontend
python -m build
pip install dist/preswald*.tar.gz
cd tests/"$example" && preswald run