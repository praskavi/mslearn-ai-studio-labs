import os
from dotenv import load_dotenv
from pathlib import Path

# import namespaces
from openai import OpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider


def main(): 
    try:
        # Get configuration settings from the .env file beside this script.
        app_dir = Path(__file__).resolve().parent
        load_dotenv(app_dir / ".env")
        azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        model_deployment = os.getenv("MODEL_DEPLOYMENT")
        if not azure_openai_endpoint or not model_deployment:
            raise ValueError("AZURE_OPENAI_ENDPOINT and MODEL_DEPLOYMENT must be set in .env")

        # Initialize the OpenAI client
        token_provider = get_bearer_token_provider(
        DefaultAzureCredential(), "https://ai.azure.com/.default"
        )   
    
        openai_client = OpenAI(
            base_url=azure_openai_endpoint,
            api_key=token_provider
        )


        # Track the previous response so follow-up prompts keep their context.
        last_response_id = None

        # Loop until the user wants to quit
        while True:
            input_text = input('\nEnter a prompt (or type "quit" to exit): ')
            if input_text.lower() == "quit":
                break
            if len(input_text) == 0:
                print("Please enter a prompt.")
                continue

            # Get and display a response for the current prompt- ChatCompletions API
            # completion = openai_client.chat.completions.create(
            #     model=model_deployment,
            #     messages=[
            #         {
            #             "role": "system",
            #             "content": "You are a helpful AI assistant that answers questions and provides information."
            #         },
            #         {
            #             "role": "user",
            #             "content": input_text
            #         }
            #     ]
            # )
            # print(f"\nAssistant: {completion.choices[0].message.content}", flush=True)
            
            # Get and display a response for the current prompt using the response API
            # Track responses
            # last_response_id = None
            response = openai_client.responses.create(
                model=model_deployment,
                # simpler syntax in which the system message is assigned to the instructions parameter
                instructions = "You are a helpful AI assistant that answers questions and provides information.",
                # the user prompt is assigned to the input parameter.
                input=input_text,
                stream=True,
                previous_response_id=last_response_id
            )
            # print(response.output_text)
            # last_response_id = response.id
            for event in response:
                if event.type == "response.output_text.delta":
                    print(event.delta, end="")
                elif event.type == "response.completed":
                    last_response_id = event.response.id

            print()

    except Exception as ex:
        print(ex)

if __name__ == '__main__': 
    main()
