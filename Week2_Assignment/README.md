# Week 2 Assignment

This folder practices building generative AI applications with the Azure OpenAI-compatible OpenAI client. The examples use Microsoft Entra ID authentication, the Responses API, conversation state, streaming, asynchronous requests, and model tools.

## Projects

### 1. Foundry chat application

Location: `foundry-chat/python/chat-app/`

Files:

- `chat-app.py` is the synchronous streaming example.
- `chat-async.py` is the asynchronous Responses API example.
- `requirements.txt` lists the Python packages for both examples.

#### Concepts practiced

- Calling an Azure OpenAI model through the OpenAI Python SDK.
- Authenticating with `DefaultAzureCredential` instead of putting an API key in source code.
- Using a Microsoft Entra bearer-token provider with the OpenAI client.
- Supplying system behavior with the Responses API `instructions` parameter.
- Maintaining conversation context with `previous_response_id`.
- Streaming response events so text is displayed while the model is generating it.
- Using asynchronous clients and cleaning up asynchronous resources.
- Comparing the newer Responses API with the commented Chat Completions API example.

#### Inputs

The application accepts prompts typed at the console. The following settings are loaded from a `.env` file:

```env
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/openai/v1
MODEL_DEPLOYMENT=your-deployment-name
```

`MODEL_DEPLOYMENT` must be the deployment name in Azure, not only the base model name. Azure credentials are obtained from the local Azure identity chain, such as an Azure CLI login, Visual Studio Code sign-in, managed identity, or another supported credential source.

#### Outputs

- `chat-app.py` prints each streamed text delta as it arrives and then starts a new prompt.
- `chat-async.py` prints the completed assistant response after the awaited request finishes.
- The response ID is retained in memory so follow-up prompts can use the same conversation context.
- Enter `quit` to stop either program.

#### Logic flow

1. Load the endpoint and deployment name from `.env`.
2. Create a Microsoft Entra token provider with `DefaultAzureCredential`.
3. Configure `OpenAI` for the Azure endpoint (`AsyncOpenAI` in the async version).
4. Repeatedly read a prompt from the console and ignore empty prompts.
5. Send the prompt to the Responses API with the configured model and the previous response ID.
6. In `chat-app.py`, handle `response.output_text.delta` events and save the ID from `response.completed`.
7. In `chat-async.py`, await the response, print `response.output_text`, and save its ID.
8. Close the async client and credential in the `finally` block when the async program exits.

### 2. Travel tools application

Location: `tools/python/tools-app/`

Entry point: `tools-app.py`

The `brochures/` directory contains the PDF source material used by file search.

#### Concepts practiced

- Grounding model answers in private files with a vector store and the `file_search` tool.
- Combining file search with the `web_search` tool for general destination information and current travel advice.
- Uploading a batch of files and polling until processing completes.
- Maintaining multi-turn context with `previous_response_id`.
- Managing local file handles with `try/finally`.
- Validating configuration and handling runtime errors in a command-line application.

#### Inputs

The program uses:

- PDF files in `tools/python/tools-app/brochures/`.
- Questions typed at the console.
- `AZURE_OPENAI_ENDPOINT` and `MODEL_DEPLOYMENT` in `tools/python/tools-app/.env`.
- Microsoft Entra credentials available through `DefaultAzureCredential`.

#### Outputs

- A vector store is created remotely and populated with the brochure PDFs.
- The model prints a travel-assistant answer for each question.
- Answers may use brochure content through `file_search` and web results through `web_search`.
- The program prints an error message if configuration or an API operation fails.

#### Logic flow

1. Load configuration from the `.env` file beside the script.
2. Authenticate and create the Azure OpenAI-compatible `OpenAI` client.
3. Find all PDF files in `brochures/`; stop if none are present.
4. Create a vector store and upload the PDFs, waiting for the upload batch to finish.
5. Read questions until the user enters `quit`.
6. Send each question with travel-assistant instructions, the vector-store ID, and both search tools enabled.
7. Print the response text and retain the response ID for the next turn.
8. Close all opened brochure streams and report exceptions without exposing a traceback.

## Dependencies

Install the packages from the requirements file for the application you want to run:

```powershell
cd foundry-chat/python/chat-app
python -m pip install -r requirements.txt

cd ../../../tools/python/tools-app
python -m pip install -r requirements.txt
```

The packages are:

- `openai`: OpenAI-compatible client and Responses API.
- `azure-identity`: Microsoft Entra authentication and bearer-token providers.
- `python-dotenv`: Loads settings from `.env` files.
- `aiohttp`: Async HTTP support used by the asynchronous Azure identity/client path.

## Running the examples

Run each script from its application directory so relative files and environment loading behave as expected:

```powershell
cd foundry-chat/python/chat-app
python chat-app.py
python chat-async.py

cd ../../../tools/python/tools-app
python tools-app.py
```

An Azure OpenAI resource, a deployed model, appropriate permissions, and a successful Azure login are required. The travel tools example also requires at least one PDF in `brochures/`.
