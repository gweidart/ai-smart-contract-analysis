# evaluation.py

import torch
from metrics import calculate_metrics
import logging

logging.getLogger(__name__)

def evaluate_model(model, data_loader):
    """
    Evaluates the Code-BERT model on the validation set.
    :param model: The trained Code-BERT model.
    :param data_loader: DataLoader for the validation set.
    :return: None
    """
    try:
        # Move model to GPU if available
        device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        model.to(device)

        model.eval()  # Set model to evaluation mode
        all_labels = []
        all_predictions = []

        with torch.no_grad():  # Disable gradient calculation for evaluation
            with Progress() as progress:
                eval_task = progress.add_task("Evaluating...", total=len(data_loader))

                for batch_idx, (tokens, labels) in enumerate(data_loader):
                    tokens = {k: v.to(device) for k, v in tokens.items()}
                    labels = labels.to(device)

                    # Forward pass
                    outputs = model(**tokens)
                    logits = outputs.logits

                    # Apply sigmoid to logits to get predictions between 0 and 1
                    predictions = torch.sigmoid(logits)

                    # Convert predictions to binary labels (0 or 1) based on a threshold of 0.5
                    predicted_labels = (predictions > 0.5).int()

                    all_labels.append(labels.cpu())
                    all_predictions.append(predicted_labels.cpu())

                    progress.update(eval_task, advance=1)

        # Stack all the batch predictions and labels
        all_labels = torch.cat(all_labels, dim=0)
        all_predictions = torch.cat(all_predictions, dim=0)

        # Calculate evaluation metrics
        calculate_metrics(all_labels, all_predictions)

    except Exception as e:
        logging.error(f"Error during evaluation: {e}")
        raise e

# Example usage in main.py
# from evaluation import evaluate_model
# evaluate_model(model, validation_loader)
