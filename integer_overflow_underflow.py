import re
import logging
from json_saver import save_results_as_json

# Setup logging with rich handler
log = logging.getLogger(__name__)

def detect_integer_overflow_underflow(sol_content):
    """
    Detect integer overflow/underflow vulnerability in a Solidity file's content.
    
    Args:
    - sol_content (str): The content of the Solidity source code.
    
    Returns:
    - (bool): True if an integer overflow/underflow vulnerability is detected, False otherwise.
    """
    
    # 1. Detect arithmetic operations (+, -, *)
    arithmetic_operations = re.search(r'[\+\-\*]', sol_content)
    if not arithmetic_operations:
        log.info("No arithmetic operations found.")
        return False  # No integer overflow/underflow if no arithmetic operations are found
    
    log.info("Arithmetic operation found.")
    
    # 2. Detect SafeMath usage
    safe_math_usage = re.search(r'SafeMath\b', sol_content)
    if safe_math_usage:
        log.info("SafeMath library usage found. No integer overflow/underflow vulnerability.")
        return False  # No vulnerability if SafeMath is used
    
    # 3. Detect condition statements (e.g., assert, require)
    condition_statement = re.search(r'\b(assert|require)\b\s*\(.*[\+\-\*]', sol_content)
    if condition_statement:
        log.info("Condition statement (assert/require) found. No integer overflow/underflow vulnerability.")
        return False  # No vulnerability if arithmetic operations are constrained by assert/require

    # If none of the checks passed, an integer overflow/underflow vulnerability is likely
    log.warning("Integer overflow/underflow vulnerability detected.")
    return True


def label_integer_overflow_underflow(sol_files_content):
    """
    Process Solidity files and label them for integer overflow/underflow vulnerability.
    
    Args:
    - sol_files_content (dict): A dictionary of {file_path: content}.
    
    Returns:
    - results (dict): A dictionary of {file_path: label}, where label = 1 (vulnerability) or 0 (no vulnerability).
    """
    results = {}
    for file_path, content in sol_files_content.items():
        log.info(f"Processing file: {file_path}")
        has_vulnerability = detect_integer_overflow_underflow(content)
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
    
    # Label files for integer overflow/underflow vulnerability
    results = label_integer_overflow_underflow(sol_files_content)
    
    # Save the results as JSON files
    save_results_as_json(results, output_dir='json_out/integer_overflow_underflow')
