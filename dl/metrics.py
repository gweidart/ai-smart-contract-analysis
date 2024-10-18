# metrics.py

import torch
import logging
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Configure logging with Rich for better readability
logging.getLogger(__name__)

def calculate_metrics(labels, predictions):
    """
    Calculates and logs the evaluation metrics for multi-label classification.
    :param labels: Ground truth labels.
    :param predictions: Model predictions.
    :return: None
    """
    try:
        # Convert tensors to numpy arrays for metric calculation
        labels = labels.numpy()
        predictions = predictions.numpy()

        # Calculate metrics
        accuracy = accuracy_score(labels, predictions)
        precision = precision_score(labels, predictions, average='macro', zero_division=0)
        recall = recall_score(labels, predictions, average='macro', zero_division=0)
        f1 = f1_score(labels, predictions, average='macro', zero_division=0)

        # Log the metrics
        logging.info(f"Accuracy: {accuracy:.4f}")
        logging.info(f"Precision: {precision:.4f}")
        logging.info(f"Recall: {recall:.4f}")
        logging.info(f"F1 Score: {f1:.4f}")

    except Exception as e:
        logging.error(f"Error calculating metrics: {e}")
        raise e
