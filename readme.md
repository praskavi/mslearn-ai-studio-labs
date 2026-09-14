# Develop Generative AI Solutions in Azure

The exercises in this repo are designed to provide you with a hands-on learning experience in which you'll explore common tasks that developers perform when building generative AI solutions on Microsoft Azure.

> **Note**: To complete the exercises, you'll need an Azure subscription in which you have sufficient permissions and quota to provision the necessary Azure resources and generative AI models. If you don't already have one, you can sign up for an [Azure account](https://azure.microsoft.com/free). There's a free trial option for new users that includes credits for the first 30 days.

View the exercises in the [GitHub Pages site for this repo](https://go.microsoft.com/fwlink/?linkid=2310724).

> **Note**: While you can complete these exercises on their own, they're designed to complement modules on [Microsoft Learn](https://aka.ms/mslearn-generative-ai), in which you'll find a deeper dive into some of the underlying concepts on which these exercises are based.

## Tools application

The `labfiles/tools/python/tools-app/tools-app.py` script is a command-line travel assistant that uses Azure OpenAI, brochure content, and web search.

### How the code works

1. **Loads configuration**

   The script finds its own directory and loads the `.env` file from there. It reads `AZURE_OPENAI_ENDPOINT` and `MODEL_DEPLOYMENT`. The application stops with an error if either setting is missing.

2. **Creates an authenticated client**

   `DefaultAzureCredential` obtains Microsoft Entra ID credentials from the available Azure login methods. `get_bearer_token_provider` supplies access tokens to the OpenAI client, which is configured with the Azure OpenAI endpoint.

3. **Uploads travel brochures**

   The script searches the `brochures` folder for PDF files and creates a vector store named `travel-brochures`. It uploads the PDFs and waits for processing to finish. The file streams are closed after uploading, even if the upload fails.

4. **Maintains conversation context**

   `last_response_id` stores the previous response ID. Passing this ID to the next request allows the assistant to keep context across questions.

5. **Answers questions with tools**

   The application repeatedly prompts for a question until the user enters `quit`. Each question is sent to the configured model with two tools:
   - `file_search` searches the uploaded travel brochures.
   - `web_search` provides general destination information and current travel advice.

6. **Handles errors**

   The main application flow is wrapped in a `try`/`except` block so runtime errors are displayed to the user instead of producing an unhandled traceback.

### Configuration

Create a `.env` file in `labfiles/tools/python/tools-app` with the Azure endpoint and the exact deployment name created in Azure:

```env
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/openai/v1
MODEL_DEPLOYMENT=your-deployment-name
```

The `MODEL_DEPLOYMENT` value must be the deployment name, not just the model's catalog name. The `brochures` folder must contain at least one PDF file before the application can answer questions.

## Chat application APIs

The `labfiles/foundry-chat/python/chat-app/chat-app.py` sample demonstrates two OpenAI-compatible ways to generate chat responses. Both use the same `OpenAI` client, Azure endpoint, Entra ID authentication, and model deployment configured in `.env`.

### Chat Completions API

The Chat Completions API sends a list of messages and returns one completed answer:

```python
completion = openai_client.chat.completions.create(
   model=model_deployment,
   messages=[
      {"role": "system", "content": "You are a helpful AI assistant."},
      {"role": "user", "content": input_text}
   ]
)
print(completion.choices[0].message.content)
```

The response text is read from `completion.choices[0].message.content`. To preserve conversation history with this API, the application must keep the previous messages and send them again with each request.

### Responses API

The current chat application uses the newer Responses API with streaming enabled:

```python
response = openai_client.responses.create(
   model=model_deployment,
   input=input_text,
   stream=True,
   previous_response_id=last_response_id
)
```

When `stream=True`, the API returns events instead of one completed response. The application prints each `response.output_text.delta` event as it arrives, which makes the answer visible incrementally:

```python
for event in response:
   if event.type == "response.output_text.delta":
      print(event.delta, end="")
   elif event.type == "response.completed":
      last_response_id = event.response.id
```

The completed response ID is saved and sent as `previous_response_id` on the next request. This lets the Responses API maintain context without manually rebuilding the full message list. The response ID must be read from `event.response.id` when streaming; the stream object itself does not have an `id` property.

### Choosing between the APIs

- Use **Chat Completions** for the familiar message-based interface and explicit control over the complete conversation history.
- Use **Responses** for newer features, response chaining, streaming events, and a unified input format.
- Use only one API call path at a time in the sample. The Chat Completions code is commented out while the streaming Responses API is active.

### Asynchronous chat application

The `labfiles/foundry-chat/python/chat-app/chat-async.py` sample uses the asynchronous versions of the same components:

- `AsyncOpenAI` sends requests without blocking the event loop.
- `azure.identity.aio.DefaultAzureCredential` provides an asynchronous Azure credential.
- `get_bearer_token_provider` creates an awaitable token provider for `AsyncOpenAI`.
- `aiohttp` provides the asynchronous HTTP transport used by the Azure credential.

The response request must be awaited:

```python
response = await openai_client.responses.create(
   model=model_deployment,
   input=input_text,
   previous_response_id=last_response_id
)
```

The async token provider is important. A synchronous provider returns a plain string, while `AsyncOpenAI` awaits the provider internally. Awaiting a string causes `object str can't be used in 'await' expression`.

Because both the OpenAI client and Azure credential create asynchronous HTTP resources, both must be closed when the application exits:

```python
finally:
   await openai_client.close()
   await credential.close()
```

The async dependencies are listed in `labfiles/foundry-chat/python/chat-app/requirements.txt`. Install them into the selected virtual environment before running the async sample:

```powershell
python -m pip install -r labfiles/foundry-chat/python/chat-app/requirements.txt
```

## Reporting issues

If you encounter any problems in the exercises, please report them as **issues** in this repo.
