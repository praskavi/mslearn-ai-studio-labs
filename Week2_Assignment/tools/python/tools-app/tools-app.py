import os
from dotenv import load_dotenv
from pathlib import Path

# import namespaces
from openai import OpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider


# Run the travel assistant application.
def main():
    # Prepare the console for a fresh session.
    os.system('cls' if os.name == 'nt' else 'clear')

    try:
        # Load configuration from the .env file beside this script.
        app_dir = Path(__file__).resolve().parent
        load_dotenv(app_dir / ".env")
        azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        model_deployment = os.getenv("MODEL_DEPLOYMENT")

        # Stop early when required Azure OpenAI settings are missing.
        if not azure_openai_endpoint or not model_deployment:
            raise ValueError("AZURE_OPENAI_ENDPOINT and MODEL_DEPLOYMENT must be set in .env")

        # Create an Azure credential provider and configure the OpenAI client.
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(), "https://ai.azure.com/.default"
        )
        openai_client = OpenAI(
            base_url=azure_openai_endpoint,
            api_key=token_provider
        )

        # Find brochure files and upload them to a searchable vector store.
        brochure_files = list((app_dir / "brochures").glob("*.pdf"))
        if not brochure_files:
            print("No PDF files found in the brochures folder!")
            return
# Create vector store and upload files
        print("Creating vector store and uploading files...")
        vector_store = openai_client.vector_stores.create(name="travel-brochures")
        with_file_streams = [open(file_path, "rb") for file_path in brochure_files]
        try:
            file_batch = openai_client.vector_stores.file_batches.upload_and_poll(
                vector_store_id=vector_store.id,
                files=with_file_streams
            )
        finally:
            for file_stream in with_file_streams:
                file_stream.close()
        print(f"Vector store created with {file_batch.file_counts.completed} files.")

        # Track the previous response so the conversation keeps its context.
        last_response_id = None

        # Read questions and answer them until the user exits.
        while True:
            input_text = input('\nEnter a question (or type "quit" to exit): ')
            if input_text.lower() == "quit":
                break
            if len(input_text) == 0:
                print("Please enter a question.")
                continue

            # Ask the model to use brochure search and web search as needed.
            response = openai_client.responses.create(
                model=model_deployment,
                instructions="""
                You are a travel assistant that provides information on travel services available from Margie's Travel.
                Answer questions about services offered by Margie's Travel using the provided travel brochures.
                Search the web for general information about destinations or current travel advice.
                """,
                input=input_text,
                previous_response_id=last_response_id,
                tools=[
                    {
                        "type": "file_search",
                        "vector_store_ids": [vector_store.id]
                    },
                    {
                        "type": "web_search"
                    }
                ]
            )
            print(response.output_text)
            last_response_id = response.id

    # Display an application error without exposing a traceback to the user.
    except Exception as ex:
        print(ex)

# Start the application when this file is run directly.
if __name__ == '__main__': 
    main()
