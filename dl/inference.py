# inference.py

import torch
from tokenizer import SolidityTokenizer
from model_saving import load_model_checkpoint
import logging

# Configure logging with Rich for better readability
logging.getLogger(__name__)

def run_inference(model_checkpoint, solidity_file, threshold=0.5):
    """
    Runs inference on a new Solidity file to predict vulnerabilities.
    :param model_checkpoint: Path to the saved model checkpoint.
    :param solidity_file: Path to the Solidity file to analyze.
    :param threshold: Threshold to classify probabilities into binary predictions (default 0.5).
    :return: Dictionary containing predictions for each vulnerability type.
    """
    try:
        # Step 1: Load the trained model from checkpoint
        logging.info(f"Loading model from checkpoint: {model_checkpoint}")
        model_instance = VulnerabilityDetectionModel()
        model = model_instance.get_model()
        _, model, _ = load_model_checkpoint(model_checkpoint, model)

        # Set the model to evaluation mode
        model.eval()

        # Step 2: Tokenize the new Solidity code
        tokenizer = SolidityTokenizer()
        with open(solidity_file, 'r') as f:
            solidity_code = f.read()
        
        tokens = tokenizer.tokenize_code(solidity_code)

        # Step 3: Run inference
        logging.info("Running inference on the Solidity file...")
        with torch.no_grad():
            # Model expects inputs to be on CPU
            outputs = model(**tokens)
            logits = outputs.logits

            # Apply sigmoid to convert logits to probabilities
            probabilities = torch.sigmoid(logits)

            # Convert probabilities to binary predictions using the threshold
            predictions = (probabilities > threshold).int()

            # Vulnerabilities
            vulnerabilities = {
                "timestamp_dependence": bool(predictions[0][0]),
                "reentrancy": bool(predictions[0][1]),
                "integer_overflow": bool(predictions[0][2]),
                "delegatecall": bool(predictions[0][3])
            }

        logging.info(f"Predictions: {vulnerabilities}")
        return vulnerabilities

    except Exception as e:
        logging.error(f"Error during inference: {e}")
        raise e

# Example usage in main.py
# from inference import run_inference
# predictions = run_inference("checkpoint_epoch_3.pth", "path/to/new/solidity_file.sol")
