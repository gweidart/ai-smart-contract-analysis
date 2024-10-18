import os
import logging
from rich.progress import Progress

def setup_directories(solidity_root: str, json_root: str):
    """
    Setup the project directories, ensuring that both the Solidity files and JSON files
    have mirrored subdirectories.
    """
    for subdir in os.listdir(solidity_root):
        json_subdir = os.path.join(json_root, subdir)
        if not os.path.exists(json_subdir):
            os.makedirs(json_subdir)
            logging.info(f"Created directory: {json_subdir}")

def verify_dataset(solidity_root: str, json_root: str):
    """
    Verify that for each .sol file in the solidity_root, there exists a corresponding .json file in the json_root.
    If a corresponding .json file is not found, log the mismatch.
    """
    mismatches = []
    
    with Progress() as progress:
        verify_task = progress.add_task("Verifying Dataset...", total=47_000)
        
        for root, dirs, files in os.walk(solidity_root):
            for file in files:
                if file.endswith('.sol'):
                    # Get the relative path of the .sol file from the solidity root
                    rel_path = os.path.relpath(os.path.join(root, file), solidity_root)
                    
                    # Construct the corresponding .json file path in the json_root
                    json_file = os.path.join(json_root, rel_path.replace('.sol', '.json'))
                    
                    # Check if the corresponding .json file exists
                    if not os.path.exists(json_file):
                        mismatches.append(rel_path)
                    
                    # Update progress bar
                    progress.update(verify_task, advance=1)

    if mismatches:
        logging.error(f"Found mismatches between .sol and .json files: {mismatches}")
    else:
        logging.info("All Solidity files have corresponding JSON labels.")
