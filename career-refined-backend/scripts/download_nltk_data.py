import nltk
import os
from nltk.data import find

def download_nltk_data():
    """Download necessary NLTK data if not already present."""
    # Specify the download directory relative to the services directory
    nltk_data_dir = "C:/Users/rusht/Desktop/career-refined/career-refined-backend/nltk_data"  # Go up one level to services
    os.makedirs(nltk_data_dir, exist_ok=True)  # Create the directory if it doesn't exist

    # Set the NLTK data path
    nltk.data.path.append(nltk_data_dir)
    # Download stopwords
    try:
        print("Checking for stopwords...")
        find("corpora/stopwords.zip")
        print("Stopwords found.")
    except LookupError:
        print("Stopwords not found. Downloading...")
        nltk.download("stopwords", download_dir=nltk_data_dir)
        print("Stopwords downloaded.")

    # Download punkt tokenizer
    try:
        print("Checking for punkt tokenizer...")
        find("tokenizers/punkt")
        print("Punkt tokenizer found.")
    except LookupError:
        print("Punkt tokenizer not found. Downloading...")
        nltk.download("punkt", download_dir=nltk_data_dir)
        print("Punkt tokenizer downloaded.")

# Call the download function
if __name__ == "__main__":
    download_nltk_data()