# data_preprocessing.py

import torch
from torch.utils.data import Dataset, DataLoader
from tokenizer import SolidityTokenizer

class SolidityDataset(Dataset):
    def __init__(self, data, tokenizer: SolidityTokenizer, max_length: int = 512):
        """
        Custom dataset class for Solidity code and vulnerability labels.
        :param data: List of tuples (solidity_code, labels)
        :param tokenizer: Instance of SolidityTokenizer for tokenizing the code.
        :param max_length: Maximum length for tokenized input.
        """
        self.data = data
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        solidity_code, labels = self.data[idx]
        
        # Tokenize the Solidity code correctly
        tokens = self.tokenizer.tokenize_code(solidity_code, max_length=self.max_length)
        
        # Convert labels (True/False) into integers (1/0) for model training
        label_tensor = torch.tensor([
            int(labels["timestamp_dependence"]),
            int(labels["reentrancy"]),
            int(labels["integer_overflow"]),
            int(labels["delegatecall"])
        ])
        
        return tokens, label_tensor

def create_data_loader(data, tokenizer: SolidityTokenizer, batch_size: int = 16, max_length: int = 512, num_workers: int = 0):
    """
    Creates a PyTorch DataLoader for batching the Solidity data.
    :param data: The list of tuples (solidity_code, labels).
    :param tokenizer: An instance of SolidityTokenizer.
    :param batch_size: Size of each batch for training (default 16).
    :param max_length: Maximum length for tokenized input.
    :param num_workers: Number of workers for data loading (default 0 for CPU-only training).
    :return: DataLoader object for PyTorch.
    """
    dataset = SolidityDataset(data, tokenizer, max_length=max_length)
    return DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers)
