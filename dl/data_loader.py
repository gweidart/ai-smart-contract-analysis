import os
import json
import logging
from rich.progress import Progress

def load_solidity_files(solidity_root: str):
    """
    Generator that yields Solidity files from the dataset.
    Returns the full path to the Solidity file and its relative path from the root.
    """
    for root, dirs, files in os.walk(solidity_root):
        for file in files:
            if file.endswith('.sol'):
                # Return both the full path and the relative path for folder structure preservation
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, solidity_root)
                yield full_path, rel_path

def load_solidity_and_labels(solidity_root: str, json_root: str):
    """
    Loads Solidity files and their corresponding vulnerability labels from JSON files.
    Preserves the folder structure when loading .json files.
    
    Returns a list of tuples containing:
    (solidity_code, labels_dict)
    """
    data = []
    
    with Progress() as progress:
        file_task = progress.add_task("Loading Solidity files and labels...", total=47_000)
        
        for solidity_file, rel_path in load_solidity_files(solidity_root):
            # Preserve the folder structure for the corresponding .json file
            json_file = os.path.join(json_root, rel_path.replace('.sol', '.json'))
            
            # Check if the corresponding .json file exists
            if not os.path.exists(json_file):
                logging.warning(f"Skipping {solidity_file}: Corresponding JSON file not found ({json_file})")
                continue

            try:
                with open(solidity_file, 'r') as sol_file:
                    solidity_code = sol_file.read()

                with open(json_file, 'r') as json_file_obj:
                    labels = json.load(json_file_obj)
                    
                # Ensure that the JSON labels follow the expected structure
                if not all(k in labels for k in ["timestamp_dependence", "reentrancy", "integer_overflow", "delegatecall"]):
                    logging.error(f"Incorrect label format in {json_file}, skipping this file.")
                    continue

                # Add the solidity code and corresponding labels to the data list
                data.append((solidity_code, labels))
                
            except json.JSONDecodeError as e:
                logging.error(f"JSON decode error in {json_file}: {e}, skipping this file.")
            except Exception as e:
                logging.error(f"Error loading files: {e}, skipping this file.")
            
            progress.update(file_task, advance=1)

    logging.info(f"Loaded {len(data)} Solidity files with corresponding labels.")
    return data
