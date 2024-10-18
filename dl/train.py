# train.py

import torch
from torch.optim import AdamW
from transformers import get_scheduler
from rich.progress import Progress
import logging

# Configure logging with Rich for better readability
logging.getLogger(__name__)

def train_model(model, data_loader, epochs: int = 3, learning_rate: float = 5e-5):
    """
    Trains the Code-BERT model on the tokenized Solidity dataset.
    :param model: The initialized Code-BERT model.
    :param data_loader: DataLoader for batching the tokenized dataset.
    :param epochs: Number of training epochs (default: 3).
    :param learning_rate: Learning rate for AdamW optimizer (default: 5e-5).
    """
    try:
        # Set up the optimizer and learning rate scheduler
        optimizer = AdamW(model.parameters(), lr=learning_rate)
        num_training_steps = epochs * len(data_loader)
        lr_scheduler = get_scheduler(
            name="linear", optimizer=optimizer, num_warmup_steps=0, num_training_steps=num_training_steps
        )

        # Move model to CPU
        device = torch.device("cpu")
        model.to(device)
        
        # Loss function for multi-label classification
        criterion = torch.nn.BCEWithLogitsLoss()

        # Progress tracking
        with Progress() as progress:
            epoch_task = progress.add_task("Training...", total=num_training_steps)

            # Training loop
            for epoch in range(epochs):
                logging.info(f"Epoch {epoch + 1}/{epochs}")

                model.train()
                total_loss = 0
                
                for batch_idx, (tokens, labels) in enumerate(data_loader):
                    # Log the structure of the first batch before squeezing for debugging purposes
                    if batch_idx == 0:
                        logging.info(f"✨ Tokenized batch structure (before squeeze): {tokens}")
                        logging.info(f"🏷️ Labels: {labels}")

                    # Remove extra dimensions from tokenized inputs
                    tokens = {k: v.squeeze(1).to(device) for k, v in tokens.items()}
                    labels = labels.to(device)

                    # Log the structure of the first batch after squeezing for debugging purposes
                    if batch_idx == 0:
                        logging.info(f"✨ Tokenized batch structure (after squeeze): {tokens}")

                    # Forward pass
                    outputs = model(**tokens)
                    logits = outputs.logits

                    # Compute loss
                    loss = criterion(logits, labels.float())
                    total_loss += loss.item()

                    # Backpropagation
                    optimizer.zero_grad()
                    loss.backward()
                    optimizer.step()
                    lr_scheduler.step()

                    # Update progress
                    progress.update(epoch_task, advance=1)

                avg_loss = total_loss / len(data_loader)
                logging.info(f"Epoch {epoch + 1} complete. Avg loss: {avg_loss:.4f}")

        logging.info("✅ Training complete.")
    except Exception as e:
        logging.error(f"Error during training: {e}")
        raise e
