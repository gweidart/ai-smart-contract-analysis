import argparse
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.progress import Progress, SpinnerColumn, BarColumn, TimeElapsedColumn
from rich.logging import RichHandler
import threading
import os

from file_loader import discover_sol_files, load_sol_file
from remove_comments import remove_comments
from timestamp_dependence import detect_timestamp_dependence
from reentrance_detection import detect_reentrancy_vulnerability
from integer_overflow_underflow import detect_integer_overflow_underflow
from delegatecall_detection import detect_delegatecall_vulnerability
from json_saver import save_results_as_json

# Thread lock for progress updates to ensure thread safety
progress_lock = threading.Lock()

def setup_logger(quiet_mode):
    """
    Setup the root logger to adjust verbosity based on quiet mode.
    """
    # Determine the logging level based on quiet mode
    level = logging.ERROR if quiet_mode else logging.DEBUG

    # Configure the root logger
    logging.basicConfig(
        level=level,
        format="%(levelname)s - %(name)s - %(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, level=logging.NOTSET)]
    )

    # Get the root logger
    logger = logging.getLogger()

    # Prevent adding multiple handlers if setup_logger is called multiple times
    if len(logger.handlers) > 1:
        logger.handlers = [handler for handler in logger.handlers if isinstance(handler, RichHandler)]

    return logger

def process_file(file_path, progress_task, progress, logger):
    """
    Process a single Solidity file, remove comments, and run all vulnerability detections.
    """
    try:
        # Load the file content
        sol_content = load_sol_file(file_path)
        if sol_content is None:
            logger.warning(f"Could not load file: {file_path}")
            return None  # Skip if the file could not be loaded

        # Remove comments from the file
        cleaned_content = remove_comments(sol_content)

        # Detect vulnerabilities
        timestamp_label = detect_timestamp_dependence(cleaned_content)
        reentrancy_label = detect_reentrancy_vulnerability(cleaned_content)
        integer_overflow_label = detect_integer_overflow_underflow(cleaned_content)
        delegatecall_label = detect_delegatecall_vulnerability(cleaned_content)

        # Combine results into one dictionary
        results = {
            "timestamp_dependence": timestamp_label,
            "reentrancy": reentrancy_label,
            "integer_overflow": integer_overflow_label,
            "delegatecall": delegatecall_label
        }

        # Recreate original directory structure in the output directory
        relative_path = os.path.relpath(file_path, "datast")  # Get the relative path from "datast"
        output_dir = os.path.join("json_out", os.path.dirname(relative_path))  # Recreate the directory structure
        file_name = os.path.splitext(os.path.basename(file_path))[0]  # Use the contract file name without extension

        # Save the consolidated JSON result for each contract
        save_results_as_json(results, output_dir, file_name)

        # Update progress in a thread-safe manner
        with progress_lock:
            progress.advance(progress_task)

    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}")
        return None

    return file_path

def main(quiet_mode):
    root_directory = "datast"

    # Setup the logger based on the quiet mode flag
    logger = setup_logger(quiet_mode)
    
    num_threads = os.cpu_count() if os.cpu_count() else 4  # Automatically detect the number of threads based on CPU cores

    # Setup the progress bar
    with Progress(
        SpinnerColumn(),
        BarColumn(),
        "[progress.description]{task.description}",
        TimeElapsedColumn(),
        transient=True
    ) as progress:
        
        # Task 1: Discover all .sol files in the dataset directory
        logger.warning("Discovering Solidity files...")
        discovery_task = progress.add_task("[blue]Discovering Solidity files...", total=None)
        sol_files = discover_sol_files(root_directory)
        progress.update(discovery_task, completed=100)
        logger.warning(f"Discovered {len(sol_files)} Solidity files.")

        # Task 2: Multithreading to process all files
        logger.warning(f"Processing Solidity files with {num_threads} threads...")
        process_task = progress.add_task("[blue]Processing Solidity files...", total=len(sol_files))
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            # Pass the logger to each thread
            futures = {
                executor.submit(process_file, file, process_task, progress, logger): file
                for file in sol_files
            }
            
            for future in as_completed(futures):
                file = futures[future]
                try:
                    result = future.result()
                    if result:
                        logger.info(f"Completed processing for {file}")
                except Exception as e:
                    logger.error(f"Error occurred while processing {file}: {e}")

        logger.warning("Processing complete. Results have been saved to the json_out directory.")

if __name__ == "__main__":
    # Setup argument parser
    parser = argparse.ArgumentParser(description="Solidity vulnerability detection script.")
    parser.add_argument('-q', '--quiet', action='store_true', help="Suppress log output except for warnings and errors.")
    
    args = parser.parse_args()
    
    # Run the main function with the quiet mode flag
    main(quiet_mode=args.quiet)
