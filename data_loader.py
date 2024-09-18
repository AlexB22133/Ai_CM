import os
from bs4 import BeautifulSoup
from langchain.docstore.document import Document
import json

def format_url_from_filename(filename):
    """Generate a URL from the filename by replacing underscores and adjusting the format."""
    # Remove 'https___' and '.html' from the filename and replace underscores with slashes
    base_path = filename.replace("https___", "").replace(".html", "")
    base_path = base_path.replace("_", "/")
    
    # Construct the base URL using the modified filename
    base_url = f"https://developer.criticalmanufacturing.com/{base_path}/"  # Ensure trailing slash
    base_url = base_url.replace(':/', '://').replace('//', '/')  # Ensure correct URL formatting
    return base_url

def extract_urls_from_html(content):
    """Extract all URLs from HTML content along with their associated text."""
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(content, 'html.parser')
    
    # Dictionary to store the extracted URLs
    urls = {}
    
    # Loop through all anchor tags (<a>) that have an href attribute
    for a in soup.find_all('a', href=True):
        text = a.get_text().strip()  # Extract the text associated with the link
        href = a['href']  # Extract the URL from the href attribute
        
        # Skip empty or fragment-only links (starting with '#')
        if text and href and not href.startswith('#'):
            # Process internal URLs that need to be adjusted
            if href.startswith('/developer/criticalmanufacturing/com/'):
                href = href.replace('/developer/criticalmanufacturing/com/', '/')
            # For relative paths, prepend the base URL
            elif not href.startswith('http'):
                href = f"https://developer.criticalmanufacturing.com/{href.lstrip('/')}"
            
            # Ensure proper formatting of the final URL
            href = href.replace(':/', '://').replace('//', '/')
            urls[text] = href  # Add the link text and URL to the dictionary
    
    # Return the dictionary of URLs with associated text
    return urls

def load_html_files_to_chroma(vector_store, source_folder='SourceFiles'):
    """Load HTML files from the source folder into the vector store."""
    # Check if the source folder exists
    if not os.path.exists(source_folder):
        print(f"Source folder {source_folder} does not exist.")
        return

    # Get a list of all HTML files in the source folder
    html_files = [f for f in os.listdir(source_folder) if f.endswith('.html')]
    
    # List to store Document objects created from the HTML files
    documents = []

    # Loop through each HTML file in the folder
    for html_file in html_files:
        # Create the full path to the HTML file
        file_path = os.path.join(source_folder, html_file)
        
        # Generate the base URL from the filename using the format_url_from_filename function
        base_url = format_url_from_filename(html_file)

        # Open and read the contents of the HTML file
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()  # Read the file's content as a string
            
            # Parse the content using BeautifulSoup to extract the text and URLs
            soup = BeautifulSoup(content, 'html.parser')
            text_content = soup.get_text()  # Extract the plain text from the HTML
            urls = extract_urls_from_html(content)  # Extract URLs and their associated text

            # Ensure that the "More Info" URL is included, defaulting to the base URL if missing
            more_info_url = urls.get('More Info', base_url)
            more_info_url = more_info_url if more_info_url.startswith('http') else f"https://{more_info_url}"
            urls['More Info'] = more_info_url  # Add or update the "More Info" link in the URLs dictionary

            # If no URLs were found, use the base URL as the fallback for "source_urls"
            if not urls:
                urls = {"More Info": base_url}  # Fallback to base URL if no URLs are found

            # Convert the URLs dictionary to a JSON string to store in metadata
            source_urls_json = json.dumps(urls)

            # Create a metadata dictionary for the Document object
            document_metadata = {
                "base_url": base_url,  # Include the base URL
                "filename": html_file,  # Include the filename for reference
                "source_urls": source_urls_json  # Store extracted URLs as a JSON string
            }
            
            # Create a Document object containing the extracted text and metadata
            document = Document(page_content=text_content, metadata=document_metadata)
            
            # Append the Document object to the list of documents
            documents.append(document)

    # Add all the documents to the vector store
    vector_store.add_documents(documents)
    
    # Print status messages indicating success
    print(f"Loaded {len(documents)} documents into the vector store.")
    print("Data loading completed successfully.")



    #I'd be happy to help! To subscribe to a report in SQL Server Reporting Services (SSRS), follow these steps: 
    # Navigate to the SSRS folder where the report is located and select "Subscribe" from the drop-down menu.
    # In the subscription page, provide the following details:
    # * The delivery method * The file name * The file path (where the report will be stored after it's generated). It's strongly recommended to use a shared folder. * The render format (XML, CSV, PDF, HTML, ...) * Credentials necessary to access the file path * The schedule options * The collection of values for the report parameters
    # Press "OK" to save the subscription.
    # For more information on how to subscribe to reports, please refer to the article: Subscriptions and Delivery (Reporting Services) ⧉

#For more information: https://developer.criticalmanufacturing.com/analytics/subscribereports/
# 👤
#How to create custom data warehouse cubes?
# 🤖
# To create a new cube or dimension in the Critical Manufacturing Data Warehouse solution, follow these steps:
# If not yet installed, install Visual Studio 2012 with the BIDS (Business Intelligence Development Studio) option checked.
# Start Visual Studio 2012, choose File -> New… -> Project. Select “Business Intelligence Projects” as Project Type and then “Import Analysis Services 2012 Database”. Finally name your project, e.g. CriticalManufacturingMESASProject and press OK.
# In the next screen, type the CriticalManufacturingMES Analysis Services Database server and name and select Next.
# An import status window will appear. Please wait for the import process to complete. You should then see a window as shown in the next figure.
# Finally, press Finish. You should now have the CriticalManufacturingMES Analysis Services Project ready to add new dimensions, aggregations or calculations.
# Before making any change to the project, please read the following SQL Server online entry:Working with Analysis Services Projects and Databases in a Production Environment ⧉For more information on Analysis Services Projects, please follow these links:- Defining an Analysis Services Project ⧉- Defining an Analysis Services Database ⧉

# For more information: https://developer.criticalmanufacturing.comhttps://developer.criticalmanufacturing.com//developer/criticalmanufacturing/com/analytics/customdatawarehousecubes// 