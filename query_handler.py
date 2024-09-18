from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
import json
import re

def handle_query(vector_store, embedding, llm, question, chat_history):
    # Check if the embedding model is available
    if embedding is None:
        raise Exception("Embedding model is not available")

    # Perform a similarity search in the vector store using the user's question
    results = vector_store.similarity_search(question, k=2)

    # Initialize an empty list to hold context messages and set default values for URLs
    context_messages = []
    base_url = "https://developer.criticalmanufacturing.com"  # Default base URL if no better one is found
    more_info_url = None  # This will store the "More Info" URL if found

    # Loop through the results from the similarity search
    for result in results:
        # Append the content of the result to the context_messages list
        context_messages.append(("system", result.page_content))  # The AI uses this context for answering
        
        # Extract metadata from the result
        metadata = result.metadata
        if not metadata:
            continue  # Skip if no metadata is found

        # Try to extract the "More Info" URL from the "source_urls" in metadata
        if "source_urls" in metadata:
            try:
                # Load the source URLs stored as a JSON string
                source_urls = json.loads(metadata["source_urls"])
                # Look specifically for the "More Info" link within the URLs
                more_info_url = source_urls.get("More Info", None)
            except json.JSONDecodeError as e:
                # If there's an error in decoding JSON, log the error and skip
                print(f"Error decoding JSON source_urls: {e}")
                more_info_url = None
        else:
            # If "source_urls" is not available, try to use the "source" metadata field
            if "source" in metadata:
                source_url = metadata["source"].strip()
                more_info_url = format_source_url(source_url, base_url)

        # Log metadata for debugging purposes
        print("Result metadata:", metadata)

        # Stop searching once a valid "More Info" URL is found
        if more_info_url:
            break

    # Create the system prompt for the AI model to set the assistant's behavior
    qa_system_prompt = """You are an AI Assistant that will answer questions in the context of Critical Manufacturing MES. 
    When answering, try to be polite every time. Do not say "In the context you gave me..." to start a conversation. 
    If required, make a list of steps to do something. Answer with the information you know. Do not give any href links. """

    # Prepare the prompt template that will include the context and chat history
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt),  # System message to guide AI behavior
            MessagesPlaceholder(variable_name="context"),  # Placeholder for the context of the search results
            MessagesPlaceholder(variable_name="chat_history"),  # Placeholder for chat history with the user
            ("human", "{question}")  # The actual user's question to be answered by the AI
        ]
    )

    # Create a chain to handle the retrieval process and response generation
    retriever_chain = RunnablePassthrough(
        context={"context": context_messages, "chat_history": chat_history, "question": question}
    )

    # Define the full RAG (Retrieval-Augmented Generation) chain
    rag_chain = (
        retriever_chain  # Pass the retrieved context to the chain
        | qa_prompt  # Apply the prompt template to the chain
        | llm  # Use the language model (LLM) to generate the response
    )

    # Prepare input data with context, chat history, and the question
    input_data = {
        "context": context_messages,
        "chat_history": chat_history,
        "question": question
    }

    try:
        # Invoke the chain and get the AI response
        ai_msg = rag_chain.invoke(input_data)
    except Exception as e:
        # Handle any errors that occur during the process
        print(f"Error during query handling: {e}")
        ai_msg = "An error occurred while processing your query."

    # Get the response from the AI model and strip any extra spaces
    response_message = ai_msg.content.strip()

    # Ensure proper URL formatting for the "More Info" link if available
    if more_info_url:
        # Optionally clean the URL to remove unwanted segments
        if '/developer/criticalmanufacturing/com/' in more_info_url:
            more_info_url = more_info_url.replace('/developer/criticalmanufacturing/com/', '/')
        more_info_url = clean_url(more_info_url)  # Clean the URL for common issues
        # Generate a "More Info" link to append to the response
        more_info_link = f'<br><br>For more information: <a href="{more_info_url}" target="_blank">{more_info_url}</a>'
    else:
        more_info_link = ""  # If no URL is found, don't add a link

    # Combine the AI response with the "More Info" link
    answer_with_link = f"{response_message}{more_info_link}"

    # Prepare the final response, including chat history
    response = {
        "answer": answer_with_link,
        "chat_history": chat_history
    }
    
    # Return the response with the AI's answer and the updated chat history
    return response

#  function to format source URLs correctly
def format_source_url(source_url, base_url):
    """Format source URL from metadata correctly."""
    source_url = source_url.replace("___", "/").replace("_", "/").replace(".html", "")
    if not source_url.startswith("http"):
        source_url = f"{base_url}/{source_url.lstrip('/')}"

    # Ensure the URL starts with http:// or https://
    if not source_url.startswith("http"):
        source_url = f"https://{source_url.lstrip('/')}"

    return source_url

#  function to clean URL and fix common issues
def clean_url(url):
    """Clean and fix common issues in URLs."""
    # Remove duplicate slashes
    url = re.sub(r'(?<!:)//+', '/', url)
    # Ensure URL starts with http or https
    if not url.startswith("http"):
        url = f"https://{url.lstrip('/')}"

    return url
