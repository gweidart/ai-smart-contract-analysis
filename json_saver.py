import os
import json
import logging

def save_results_as_json(results, output_dir, file_name):
    """Save results as a single JSON file, with multiple vulnerability entries."""
    try:
        # Create the directory if it does not exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logging.info(f"Created directory: {output_dir}")
        
        # Save the results in a single JSON file for each Solidity contract
        output_file = os.path.join(output_dir, f"{file_name}.json")
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=4)
        
        logging.info(f"Successfully saved results to {output_file}")

    except OSError as e:
        logging.error(f"Failed to create directory {output_dir}: {e}")
    except IOError as e:
        logging.error(f"Failed to write to file {output_file}: {e}")
    except Exception as e:
        logging.error(f"Unexpected error occurred while saving {output_file}: {e}")
