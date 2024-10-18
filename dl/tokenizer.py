# tokenizer.py

from transformers import RobertaTokenizer

class SolidityTokenizer:
    def __init__(self, model_name: str = "microsoft/codebert-base"):
        """
        Initializes the Code-BERT tokenizer.
        :param model_name: The pretrained Code-BERT model to use.
        """
        self.tokenizer = RobertaTokenizer.from_pretrained(model_name)

    def tokenize_code(self, code: str, max_length: int = 512):
        """
        Tokenizes a given piece of Solidity code.
        :param code: Solidity code to tokenize.
        :param max_length: Maximum length of tokens (default 512 for Code-BERT).
        :return: Tokenized inputs in tensor format (PyTorch).
        """
        return self.tokenizer(
            code, 
            padding="max_length", 
            truncation=True, 
            max_length=max_length, 
            return_tensors="pt"  # returns PyTorch tensors
        )
