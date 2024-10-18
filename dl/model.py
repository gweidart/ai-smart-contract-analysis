# model.py

import logging
from transformers import AutoModelForSequenceClassification

# Configure logging with Rich for better readability
logging.getLogger(__name__)

class VulnerabilityDetectionModel:
    def __init__(self, model_name: str = "microsoft/codebert-base", num_labels: int = 4):
        """
        Initializes the Code-BERT model for multi-label classification.
        :param model_name: Pretrained model to use (default: microsoft/codebert-base).
        :param num_labels: Number of output labels (default: 4 vulnerabilities).
        """
        try:
            self.model = AutoModelForSequenceClassification.from_pretrained(
                model_name, num_labels=num_labels
            )
            logging.info(f"Model initialized with {num_labels} labels.")
        except Exception as e:
            logging.error(f"Failed to initialize model: {e}")
            raise e
    
    def get_model(self):
        """
        Returns the initialized model.
        :return: Code-BERT model for sequence classification.
        """
        return self.model

# Example usage in main.py
# from model import VulnerabilityDetectionModel
# model_instance = VulnerabilityDetectionModel()
# model = model_instance.get_model()
