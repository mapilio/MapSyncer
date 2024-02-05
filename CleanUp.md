# Clean Up

### Removing the Cloned Repository:

1. Navigate to the directory where you cloned the repository using the `cd` command:

    ```bash
    cd path/to/MapSyncer
    ```

2. Remove the cloned repository using the following command:

    ```bash
    rm -rf MapSyncer
    ```

    This command will recursively delete the `MapSyncer` directory and its contents.

### Uninstalling Python Dependencies:

If you used `pip` to install the project dependencies, follow these steps:

1. Navigate to the directory where you cloned the repository using the `cd` command, if you are not already there.

2. Run the following command to uninstall the Python dependencies:

    ```bash
    pip uninstall -r requirements.txt
    ```

    This command will uninstall all the packages listed in the `requirements.txt` file.

### Cleaning up the Virtual Environment (Optional):

If you used a virtual environment to install the dependencies, you can deactivate and remove it as follows:

1. Deactivate the virtual environment:

    ```bash
    deactivate
    ```

2. Remove the virtual environment directory. The name of the virtual environment directory might be `venv`, `env`, or any other name you used. Replace `<venv_name>` with the actual name:

    ```bash
    rm -rf <venv_name>
    ```