import re
import logging

# Setup logging with rich handler
log = logging.getLogger(__name__)

def remove_comments(sol_content):
    """
    Remove single-line (//) and multi-line (/* */) comments from Solidity content.
    
    Args:
    - sol_content (str): The content of the Solidity source code.
    
    Returns:
    - (str): The Solidity source code with comments removed.
    """
    
    # Regex pattern to match single-line comments (//...) and multi-line comments (/*...*/)
    comment_pattern = re.compile(r'//.*?$|/\*.*?\*/', re.DOTALL | re.MULTILINE)
    
    # Remove comments from the Solidity content
    cleaned_content = re.sub(comment_pattern, '', sol_content)
    
    # Log the removal operation
    log.info("Comments removed from Solidity file.")
    
    return cleaned_content


def remove_comments_from_all_files(sol_files_content):
    """
    Remove comments from all Solidity files in the provided dictionary.
    
    Args:
    - sol_files_content (dict): A dictionary of {file_path: content}.
    
    Returns:
    - cleaned_files_content (dict): A dictionary of {file_path: cleaned_content}, where comments are removed.
    """
    cleaned_files_content = {}
    
    for file_path, content in sol_files_content.items():
        log.info(f"Processing file to remove comments: {file_path}")
        cleaned_content = remove_comments(content)
        cleaned_files_content[file_path] = cleaned_content
    
    return cleaned_files_content


# Example usage:
if __name__ == "__main__":
    from file_loader import discover_sol_files, load_all_sol_files
    
    # Discover Solidity files
    root_directory = "datast"
    sol_files = discover_sol_files(root_directory)
    
    # Load contents of Solidity files
    sol_files_content = load_all_sol_files(sol_files)
    
    # Remove comments from all files
    cleaned_sol_files_content = remove_comments_from_all_files(sol_files_content)
    
    # Now cleaned_sol_files_content contains Solidity files with comments removed
