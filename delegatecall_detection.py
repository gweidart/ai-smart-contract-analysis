import re
import logging
from json_saver import save_results_as_json

# Setup logging with rich handler
log = logging.getLogger(__name__)

def detect_delegatecall_vulnerability(sol_content):
    """
    Detect delegatecall vulnerability in a Solidity file's content.
    
    Args:
    - sol_content (str): The content of the Solidity source code.
    
    Returns:
    - (bool): True if a delegatecall vulnerability is detected, False otherwise.
    """
    
    # 1. Detect delegatecall invocation
    delegatecall_invoc = re.search(r'\bdelegatecall\b', sol_content)
    if not delegatecall_invoc:
        log.info("No delegatecall invocation found.")
        return False  # No delegatecall vulnerability if delegatecall is not found
    
    log.info("delegatecall invocation found.")
    
    # 2. Check if the caller is the owner
    owner_check = re.search(r'\bmodifier\s+onlyOwner\b|\bonlyOwner\b', sol_content)
    if owner_check:
        log.info("Owner check (onlyOwner) found. No delegatecall vulnerability.")
        return False  # No vulnerability if onlyOwner modifier is found

    # If delegatecall exists and no owner check is present, it's a dangerous delegatecall
    log.warning("Dangerous delegatecall vulnerability detected.")
    return True


def label_delegatecall_vulnerability(sol_files_content):
    """
    Process Solidity files and label them for dangerous delegatecall vulnerability.
    
    Args:
    - sol_files_content (dict): A dictionary of {file_path: content}.
    
    Returns:
    - results (dict): A dictionary of {file_path: label}, where label = 1 (vulnerability) or 0 (no vulnerability).
    """
    results = {}
    for file_path, content in sol_files_content.items():
        log.info(f"Processing file: {file_path}")
        has_vulnerability = detect_delegatecall_vulnerability(content)
        label = 1 if has_vulnerability else 0
        results[file_path] = label
    
    return results


# Example usage:
if __name__ == "__main__":
    from file_loader import discover_sol_files, load_all_sol_files
    
    # Discover Solidity files
    root_directory = "datast"
    sol_files = discover_sol_files(root_directory)
    
    # Load contents of Solidity files
    sol_files_content = load_all_sol_files(sol_files)
    
    # Label files for dangerous delegatecall vulnerability
    results = label_delegatecall_vulnerability(sol_files_content)
    
    # Save the results as JSON files
    save_results_as_json(results, output_dir='json_out/delegatecall')
