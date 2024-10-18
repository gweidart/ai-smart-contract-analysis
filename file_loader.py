import os
import logging

# Setup logging with rich handler
log = logging.getLogger(__name__)

# Module to discover and load .sol files
def discover_sol_files(root_dir):
    """Recursively discover all .sol files in the root directory."""
    sol_files = []
    log.info(f"Starting to scan directory: {root_dir}")
    
    # Use simple directory walk, logging file discovery
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.sol'):
                filepath = os.path.join(dirpath, filename)
                sol_files.append(filepath)
                log.debug(f"Discovered Solidity file: {filepath}")
    
    log.info(f"Completed scanning. Found {len(sol_files)} Solidity files.")
    return sol_files

def load_sol_file(filepath):
    """Load and read the contents of a Solidity file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
        log.info(f"Successfully loaded {filepath}")
        return content
    except (OSError, IOError) as e:
        log.error(f"Error loading file {filepath}: {e}")
        return None
