import re
import logging
from json_saver import save_results_as_json

# Setup logging with rich handler
log = logging.getLogger(__name__)

def detect_reentrancy_vulnerability(sol_content):
    """
    Detect reentrancy vulnerability in a Solidity file's content.
    
    Args:
    - sol_content (str): The content of the Solidity source code.
    
    Returns:
    - (bool): True if a reentrancy vulnerability is detected, False otherwise.
    """
    
    # 1. Detect call.value invocation
    call_value_invoc = re.search(r'\bcall\.value\b', sol_content)
    if not call_value_invoc:
        log.info("No call.value invocation found.")
        return False  # No reentrancy vulnerability if call.value is not found
    
    log.info("call.value invocation found.")
    
    # 2. Check if call.value has a zero parameter
    zero_param_check = re.search(r'call\.value\s*\(\s*0\s*\)\s*', sol_content)
    if zero_param_check:
        log.info("call.value with zero parameter found. No reentrancy vulnerability.")
        return False  # No reentrancy if the call.value parameter is zero
    
    # 3. Check if balance deduction occurs before or after call.value
    balance_deduction = re.search(r'\b\w+\s*=\s*\w+\s*-\s*\w+\s*;', sol_content)  # Example pattern for balance deduction
    if not balance_deduction:
        log.info("No balance deduction found before or after call.value. Reentrancy vulnerability detected.")
        return True
    
    # 4. Check for the presence of onlyOwner modifier
    only_owner_modifier = re.search(r'\bmodifier\s+onlyOwner\b|\bonlyOwner\b', sol_content)
    if only_owner_modifier:
        log.info("onlyOwner modifier found. No reentrancy vulnerability.")
        return False
    
    # If all checks fail, reentrancy vulnerability is likely
    log.warning("Reentrancy vulnerability detected.")
    return True


def label_reentrancy_vulnerability(sol_files_content):
    """
    Process Solidity files and label them for reentrancy vulnerability.
    
    Args:
    - sol_files_content (dict): A dictionary of {file_path: content}.
    
    Returns:
    - results (dict): A dictionary of {file_path: label}, where label = 1 (vulnerability) or 0 (no vulnerability).
    """
    results = {}
    for file_path, content in sol_files_content.items():
        log.info(f"Processing file: {file_path}")
        has_vulnerability = detect_reentrancy_vulnerability(content)
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
    
    # Label files for reentrancy vulnerability
    results = label_reentrancy_vulnerability(sol_files_content)
    
    # Save the results as JSON files
    save_results_as_json(results, output_dir='json_out/reentrancy')
