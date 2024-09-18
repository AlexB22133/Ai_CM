import os  # Provides a way of interacting with the operating system (used for environment variables)
import json  # Used for parsing JSON data (to handle request/response data)
from flask import Flask, request, jsonify, send_from_directory  # Flask modules to create the web app and handle HTTP requests
from langchain_chroma import Chroma  # Chroma is a vector store used to store and retrieve embeddings
from langchain_community.embeddings.ollama import OllamaEmbeddings  # OllamaEmbeddings is used to generate embeddings from text
from langchain_community.chat_models import ChatOllama  # ChatOllama is a language model for handling chat-based queries
from langchain.memory import ConversationBufferMemory  # ConversationBufferMemory stores chat history in memory
from query_handler import handle_query  # A custom function for handling queries (imported from another file)
from dotenv import load_dotenv  # Used to load environment variables from a .env file
import logging  # Provides logging functionality to track the state of the app

# Set environment variables for LangChain (e.g., API key, tracing, project name)
os.environ['LANGCHAIN_TRACING_V2'] = 'true'
os.environ['LANGCHAIN_ENDPOINT'] = "https://api.smith.langchain.com"
os.environ['LANGCHAIN_API_KEY'] = "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"
os.environ['LANGCHAIN_PROJECT'] = "AI_CM"

# Load environment variables from a .env file
load_dotenv()  # This will load additional environment variables if they're stored in a .env file

# Set up logging to record messages and errors (INFO level logs general information)
logging.basicConfig(level=logging.INFO)

# Initialize the Flask application
app = Flask(__name__)  # 'app' is the main Flask application

# Initialize components for embeddings and chat model

try:
    # Create an instance of OllamaEmbeddings using the 'nomic-embed-text' model
    embedding = OllamaEmbeddings(model="nomic-embed-text")
except ValueError as e:
    # If there's an error loading the specific model, log the error and fall back to the default model
    logging.error(f"Error initializing embeddings: {e}")
    embedding = OllamaEmbeddings(model="default-model")

# Initialize Chroma vector store (for storing and retrieving embeddings)
vector_store = Chroma(
    collection_name="devhtml2",  # The name of the collection in the vector store
    embedding_function=embedding,  # The embedding function used to convert text to vectors
    persist_directory="./chroma_db2"  # Directory where the vector store's data is saved
)

# Initialize a memory object to store chat history between the user and the AI
memory = ConversationBufferMemory()  # This will keep track of conversation history between turns

# Initialize the language model for chat interactions
llm = ChatOllama(model="llama3")  # The chat model used for processing and responding to user questions

# Define the '/query' endpoint to handle POST requests
@app.route('/query', methods=['POST'])
def query():
    """
    Handle a POST request to the /query endpoint.
    """
    data = request.json  # Get the request data, assuming it's in JSON format
    question = data.get('question')  # Extract the 'question' field from the request
    chat_history = data.get('chat_history', [])  # Get the previous chat history, or start with an empty list

    # If no question is provided in the request, return a 400 error (Bad Request)
    if not question:
        return jsonify({"error": "No question provided"}), 400

    try:
        # Call the handle_query function to process the query and return a response
        response = handle_query(vector_store, embedding, llm, question, chat_history)

        # Add the user's question to the chat history
        chat_history.append({"role": "user", "content": question})

        # If the response contains an answer, update the chat history
        if "answer" in response:
            # Check if the AI's last response is already the same, avoid repeating responses
            if chat_history and chat_history[-1].get('role') == 'ai':
                last_ai_response = chat_history[-1].get('content')
                if last_ai_response == response.get("answer"):
                    chat_history.pop()  # Remove the last AI response if it's a duplicate

            # Add the new AI response to the chat history
            chat_history.append({"role": "ai", "content": response["answer"]})

        # Include the updated chat history and possibly a "More Info" link in the response
        response["chat_history"] = chat_history

    except Exception as e:
        # Handle any errors that occur during processing and include the error message in the response
        response = {"error": str(e)}

    # Return the response as a JSON object
    return jsonify(response)

# Serve the index.html file for the root endpoint (e.g., when visiting the home page)
@app.route('/')
def index():
    """
    Serve the index.html file for the root endpoint.
    """
    return send_from_directory('.', 'index.html')  # Serve the 'index.html' file from the current directory

# Serve static files like CSS or JS when requested
@app.route('/<path:path>')
def static_files(path):
    """
    Serve static files (e.g., CSS, JS) from the root directory.
    """
    return send_from_directory('.', path)  # Serve files from the current directory based on the given path

# If this script is run directly, start the Flask development server
if __name__ == '__main__':
    app.run(debug=True)  # Run the app in debug mode for development (auto-reloads on code changes)
