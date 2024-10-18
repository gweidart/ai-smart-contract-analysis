import re
import logging
from rich.logging import RichHandler

# Setup logging with rich handler
log = logging.getLogger(__name__)

def detect_timestamp_dependence(sol_content):
    """
    Detect timestamp dependence in a Solidity file's content.
    
    Args:
    - sol_content (str): The content of the Solidity source code.
    
    Returns:
    - (int): 1 if a timestamp dependence vulnerability is detected, 0 otherwise.
    """
    
    # 1. Detect TDInvocation - Check if block.timestamp is used
    timestamp_invoc = re.search(r'\bblock\.timestamp\b', sol_content)
    if not timestamp_invoc:
        log.info("No timestamp invocation found.")
        return False  # No need to check further if no invocation is found
    
    log.info("Timestamp invocation found.")

    # 2. Detect TDAssign - Check if block.timestamp is assigned to any variable
    timestamp_assign = re.search(r'\b\w+\s*=\s*block\.timestamp\b', sol_content)
    
    # 3. Detect TDContaminate - Check if block.timestamp affects critical operations or return statements
    contamination_patterns = [
        re.compile(r'\b(block\.timestamp\s*<[^;]+)\b'),
        re.compile(r'\b(while\s*\([^)]*block\.timestamp[^)]*\))\b'),
        re.compile(r'\b(if\s*\([^)]*block\.timestamp[^)]*\))\b'),
        re.compile(r'\breturn\s+[^;]*block\.timestamp\b'),
    ]

    contamination_found = any([pattern.search(sol_content) for pattern in contamination_patterns])

    # Check the combined pattern: TDInvocation ∧ (TDAssign ∨ TDContaminate)
    if timestamp_assign or contamination_found:
        log.warning("Timestamp dependence vulnerability detected.")
        return True
    
    log.info("No timestamp dependence vulnerability detected.")
    return False


def label_timestamp_dependence(sol_files_content):
    """
    Process Solidity files and label them for timestamp dependence vulnerability.
    
    Args:
    - sol_files_content (dict): A dictionary of {file_path: content}.
    
    Returns:
    - results (dict): A dictionary of {file_path: label}, where label = 1 (vulnerability) or 0 (no vulnerability).
    """
    results = {}
    for file_path, content in sol_files_content.items():
        log.info(f"Processing file: {file_path}")
        label = detect_timestamp_dependence(content)
        results[file_path] = label
    
    return results
