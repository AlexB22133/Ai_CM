import os
import shutil
from data_loader import load_html_files_to_chroma  # Import function for loading HTML files into Chroma
from langchain_chroma import Chroma  # Import Chroma for vector storage
from langchain_community.embeddings.ollama import OllamaEmbeddings  # Import OllamaEmbeddings for text embedding

def main():
    try:
        # Attempt to initialize the embeddings model with a specific model
        embedding = OllamaEmbeddings(model="nomic-embed-text")
    except ValueError as e:
        # If initialization fails, print the error and initialize with a default model
        print(f"Error initializing embeddings: {e}")
        embedding = OllamaEmbeddings(model="default-model")
    
    # Define the Chroma persistence directory
    persist_directory = "./chroma_db2"
    
    # Delete the existing Chroma directory to clear old data
    if os.path.exists(persist_directory):
        shutil.rmtree(persist_directory)
        print(f"Deleted existing Chroma directory: {persist_directory}")
    
    # Ensure the Chroma persistence directory exists, create it if necessary
    if not os.path.exists(persist_directory):
        os.makedirs(persist_directory)
        print(f"Created directory for Chroma persistence: {persist_directory}")
    
    try:
        # Initialize Chroma vector store
        vector_store = Chroma(
            collection_name="devhtml2",  # Name of the collection in Chroma
            embedding_function=embedding,  # Pass the embeddings model for generating vector representations
            persist_directory=persist_directory  # Directory to persist the Chroma database
        )
    except Exception as e:
        print(f"Error initializing Chroma: {e}")
        return
    
    # Ensure the source folder exists
    source_folder = './SourceFiles'
    if not os.path.exists(source_folder):
        print(f"Source folder {source_folder} does not exist.")
        return
    
    # Load HTML files into the Chroma vector store
    try:
        load_html_files_to_chroma(vector_store, source_folder=source_folder)
        print("Data loading process finished successfully.")
    except Exception as e:
        print(f"Error during data loading: {e}")

# Ensure that the main function is called when this script is executed directly
if __name__ == '__main__':
    main()
