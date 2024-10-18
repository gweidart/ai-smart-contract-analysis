# model_saving.py

import torch
import logging

# Configure logging with Rich for better readability
logging.getLogger(__name__)

def save_model_checkpoint(model, optimizer, epoch, file_path: str):
    """
    Saves the model checkpoint, including the model's state, optimizer state, and epoch number.
    :param model: The trained model to save.
    :param optimizer: The optimizer whose state needs to be saved.
    :param epoch: The epoch number (for logging or resuming training).
    :param file_path: The path where the checkpoint will be saved.
    """
    try:
        logging.info(f"Saving model checkpoint to {file_path}")
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict()
        }
        torch.save(checkpoint, file_path)
        logging.info(f"Checkpoint saved successfully at {file_path}")
    except Exception as e:
        logging.error(f"Failed to save model checkpoint: {e}")
        raise e

def load_model_checkpoint(file_path: str, model, optimizer=None):
    """
    Loads a model checkpoint from a given file and restores the model's state.
    If an optimizer is provided, its state will also be restored.
    :param file_path: Path to the checkpoint file.
    :param model: The model to load the state into.
    :param optimizer: The optimizer to restore (optional).
    :return: Loaded epoch (if available), model, and optimizer.
    """
    try:
        logging.info(f"Loading model checkpoint from {file_path}")
        checkpoint = torch.load(file_path)
        model.load_state_dict(checkpoint['model_state_dict'])
        if optimizer:
            optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        epoch = checkpoint.get('epoch', 0)
        logging.info(f"Checkpoint loaded successfully. Resuming from epoch {epoch}")
        return epoch, model, optimizer
    except Exception as e:
        logging.error(f"Failed to load model checkpoint: {e}")
        raise e

# Example usage in main.py
# from model_saving import save_model_checkpoint, load_model_checkpoint
# save_model_checkpoint(model, optimizer, epoch=3, file_path="checkpoint.pth")
# epoch, model, optimizer = load_model_checkpoint("checkpoint.pth", model, optimizer)
