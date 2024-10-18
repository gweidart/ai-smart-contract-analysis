import logging
from rich.logging import RichHandler
from directory_setup import setup_directories, verify_dataset
from data_loader import load_solidity_and_labels
from tokenizer import SolidityTokenizer
from data_preprocessing import create_data_loader
from model import VulnerabilityDetectionModel
from train import train_model
from evaluation import evaluate_model
from model_saving import save_model_checkpoint, load_model_checkpoint
from inference import run_inference

from sklearn.model_selection import train_test_split
import torch.optim as optim
import argparse

# Custom format for RichHandler: Exclude date and timestamp
LOG_FORMAT = "%(message)s"

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,   # Use the custom format here
    handlers=[RichHandler(show_time=False, show_level=False, show_path=False)]  # Customize RichHandler
)

def parse_args():
    """
    Parse command-line arguments for training or inference.
    """
    parser = argparse.ArgumentParser(description="Vulnerability detection in Solidity files using Code-BERT")
    
    # Add an argument to specify whether inference should be run
    parser.add_argument("--inference", action="store_true", help="Run inference mode with a trained model")
    parser.add_argument("--checkpoint", type=str, default=None, help="Path to model checkpoint (required for inference)")
    parser.add_argument("--solidity_file", type=str, default=None, help="Path to Solidity file (required for inference)")
    
    # Add arguments for resuming training or running the full training pipeline
    parser.add_argument("--resume_training", action="store_true", help="Resume training from a checkpoint")
    parser.add_argument("--checkpoint_file", type=str, default=None, help="Path to checkpoint file (required for resuming training)")
    
    return parser.parse_args()

def run_training_pipeline(resume_training=False, checkpoint_file=None):
    """
    Runs the full training and evaluation pipeline.
    """
    try:
        # Directories
        SOLIDITY_DIR = 'datast'
        JSON_DIR = 'json_out'

        # Step 1: Setup directories
        logging.info("Setting up directories...")
        setup_directories(SOLIDITY_DIR, JSON_DIR)

        # Step 2: Verify dataset integrity
        logging.info("Verifying dataset...")
        verify_dataset(SOLIDITY_DIR, JSON_DIR)

        # Step 3: Load Solidity files and corresponding vulnerability labels
        logging.info("Loading Solidity files and labels...")
        solidity_data = load_solidity_and_labels(SOLIDITY_DIR, JSON_DIR)

        # Step 4: Split the dataset into training and validation sets
        train_data, val_data = train_test_split(solidity_data, test_size=0.2, random_state=42)

        # Step 5: Initialize tokenizer
        logging.info("Initializing tokenizer...")
        tokenizer = SolidityTokenizer()

        # Step 6: Create data loaders for training and validation
        logging.info("Creating data loaders...")
        train_loader = create_data_loader(train_data, tokenizer, batch_size=16)
        validation_loader = create_data_loader(val_data, tokenizer, batch_size=16)

        # Step 7: Initialize model
        logging.info("Initializing the vulnerability detection model...")
        model_instance = VulnerabilityDetectionModel()
        model = model_instance.get_model()

        # Step 8: Initialize optimizer
        optimizer = optim.AdamW(model.parameters(), lr=5e-5)

        # Step 9: Load checkpoint if resuming training
        if resume_training and checkpoint_file:
            epoch, model, optimizer = load_model_checkpoint(checkpoint_file, model, optimizer)
        else:
            epoch = 0  # Start fresh if not resuming

        # Step 10: Train the model
        logging.info(f"Starting training from epoch {epoch}...")
        for e in range(epoch, epoch + 3):  # Train for 3 epochs (or more if needed)
            train_model(model, train_loader, epochs=1)  # Train for one epoch at a time
            save_model_checkpoint(model, optimizer, e+1, file_path=f"checkpoint_epoch_{e+1}.pth")

        # Step 11: Evaluate the model
        logging.info("Starting evaluation...")
        evaluate_model(model, validation_loader)

    except Exception as e:
        logging.error(f"An error occurred during training: {e}")
        raise e

def main():
    """
    Main function to either run training or inference based on the provided arguments.
    """
    args = parse_args()

    if args.inference:
        # Run inference mode
        if not args.checkpoint or not args.solidity_file:
            logging.error("For inference, you must specify both --checkpoint and --solidity_file.")
            return
        
        logging.info("Running inference...")
        predictions = run_inference(args.checkpoint, args.solidity_file)
        logging.info(f"Inference results: {predictions}")
    else:
        # Run the training pipeline (with optional resuming from checkpoint)
        run_training_pipeline(resume_training=args.resume_training, checkpoint_file=args.checkpoint_file)

if __name__ == "__main__":
    main()
