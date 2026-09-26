# Week 3 Assignment: GenAIOps

This folder is a Microsoft Foundry GenAIOps lab built around a **Trail Guide Agent**. It practices deploying Azure infrastructure, managing prompt versions, testing an agent, evaluating response quality, and monitoring model usage and latency.

## What is practiced

- Microsoft Foundry project and agent deployment.
- Infrastructure as code with Bicep and the Azure Developer CLI (`azd`).
- Microsoft Entra authentication with `DefaultAzureCredential`.
- Prompt versioning and prompt optimization.
- Stateful conversations through the Responses API.
- Batch testing with repeatable test prompts.
- Cloud evaluation with intent-resolution, relevance, and groundedness evaluators.
- OpenTelemetry tracing and Application Insights monitoring.
- Comparing prompt versions using token counts, latency, and response quality.
- GitHub Actions integration for evaluation and collaboration workflows.

## Project structure

```text
Week3_Assignment/
├── data/
│   └── trail_guide_evaluation_dataset.jsonl
├── docs/                         # Exercise walkthroughs
├── infra/                        # Bicep infrastructure definitions
├── src/
│   ├── agents/trail_guide_agent/
│   │   ├── trail_guide_agent.py  # Creates a Foundry agent version
│   │   └── prompts/              # v1, v2, v3, and optimized prompts
│   ├── evaluators/evaluate_agent.py
│   └── tests/
│       ├── interact_with_agent.py
│       ├── run_batch_tests.py
│       ├── run_monitoring.py
│       ├── check_traces.py
│       └── test-prompts/
├── azure.yaml                    # azd project configuration
├── requirements.txt
└── agent_with_functions.py       # Earlier IT-support example
```

The `docs/` folder contains the detailed lab exercises for infrastructure setup, prompt management, prompt optimization, automated evaluation, and monitoring/tracing.

## Inputs

### Environment configuration

Azure provisioning generates a root `.env` file. It is ignored by Git and must not be committed. The scripts use values such as:

```env
AZURE_AI_PROJECT_ENDPOINT=<Foundry project endpoint>
AZURE_OPENAI_ENDPOINT=<Azure OpenAI endpoint>
AGENT_NAME=trail-guide
MODEL_NAME=gpt-5.1
```

The exact model must be available in the selected Azure region. `DefaultAzureCredential` uses the current Azure CLI, VS Code, managed identity, or another supported credential source.

### Agent and prompt inputs

- `src/agents/trail_guide_agent/prompts/` contains four instruction variants: `v1`, `v2`, `v3`, and `v4_optimized_concise`.
- `src/tests/test-prompts/` contains five repeatable scenarios: day hiking, overnight camping, three-day backpacking, trail difficulty, and winter hiking.
- `data/trail_guide_evaluation_dataset.jsonl` contains 89 query, response, and ground-truth records for cloud evaluation.

### Supporting scenario files

`IT_Policy.txt`, `system_performance.csv`, and `system_performance.txt` belong to the earlier IT-support scenario and can be used as agent knowledge or analysis inputs. The current Trail Guide scripts do not automatically open those files.

## Dependencies

Install the pinned and minimum versions defined in `requirements.txt`:

- `azure-ai-projects`, `azure-identity`, and Azure management packages for Foundry access and Azure resources.
- `openai` for the OpenAI-compatible Responses and evaluation APIs.
- `azure-monitor-opentelemetry`, `azure-monitor-query`, and `opentelemetry-instrumentation-openai-v2` for telemetry and trace queries.
- `pandas`, `numpy`, `scikit-learn`, `matplotlib`, and `seaborn` for data processing and analysis support.
- `pytest` and related tools for testing; `black`, `isort`, `flake8`, and `mypy` for code quality.
- `python-dotenv` for environment configuration and `pyyaml` for automation/configuration support.

Create an environment and install them from the assignment folder:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Infrastructure and deployment flow

1. Authenticate with Azure:

   ```powershell
   azd auth login
   az login
   ```

2. From `Week3_Assignment`, provision the project:

   ```powershell
   azd up
   azd env get-values > .env
   ```

3. The Bicep templates in `infra/` create the Foundry account and project, model deployment, role assignments, Application Insights, and Log Analytics resources. Monitoring is enabled by default.
4. Set `AGENT_NAME` and `MODEL_NAME` in `.env` as needed.

## Agent creation flow

`src/agents/trail_guide_agent/trail_guide_agent.py`:

1. Loads `.env` and reads `AZURE_AI_PROJECT_ENDPOINT`.
2. Reads a prompt file from the local `prompts/` directory.
3. Creates an authenticated `AIProjectClient`.
4. Calls `agents.create_version` with the selected model and instructions.
5. Prints the created agent ID, name, and version.

Run it with:

```powershell
python src/agents/trail_guide_agent/trail_guide_agent.py
```

The checked-in `agent.yaml` identifies the `trail-guide-v1` agent and currently points to `prompts/v2_instructions.txt`; review that configuration before creating a new version.

## Testing flow

### Interactive testing

Start a conversation with the deployed agent:

```powershell
python src/tests/interact_with_agent.py
```

The script creates a conversation, adds each console message as a user item, invokes the agent by name, prints the response, and deletes the conversation when the session ends.

### Batch testing

Run the same five test prompts against the latest agent version and save captured responses under `experiments/<experiment-name>/`:

```powershell
python src/tests/run_batch_tests.py baseline
```

The output includes the prompt text, response, agent metadata, token usage, and response ID. Use a different experiment name for each prompt or model variation.

## Evaluation flow

Run the cloud evaluation pipeline:

```powershell
python src/evaluators/evaluate_agent.py
```

The script uploads or reuses the JSONL dataset, defines the evaluators, starts an asynchronous evaluation run, polls for completion, and writes a summary to `evaluation_results.txt`. The configured evaluators measure intent resolution, relevance, and groundedness on a 1-5 scale with a default passing threshold of 3.

The current result file records 89 successful items, but the service response did not return individual scores or pass rates. Treat the result as a completed run, not as evidence of a quality ranking, until the detailed scores are reviewed in the Azure AI Foundry portal.

## Monitoring and tracing flow

Run the four prompt versions against the same five test prompts:

```powershell
python src/tests/run_monitoring.py
```

The script:

1. Loads `v1`, `v2`, `v3`, and `v4_optimized_concise`.
2. Configures Azure Monitor and instruments OpenAI calls.
3. Creates a parent trace for each prompt version and a child span for each test.
4. Records duration, prompt tokens, completion tokens, and total tokens.
5. Writes the 20-row comparison to `monitoring_results.txt`.

To query the latest trace tree from Log Analytics, run:

```powershell
python src/tests/check_traces.py
```

The current monitoring data shows that `v4_optimized_concise` used fewer average tokens than `v2` and `v3`, but it did not produce a dependable latency improvement. `monitoring_observations.txt` contains the detailed interpretation and identifies the overnight-camping response as an outlier requiring further quality validation.

## Earlier IT-support example

`agent_with_functions.py` is retained from the earlier exercise. It connects to an existing Foundry agent, maintains a conversation, prints structured response content, downloads cited container files, and saves base64-encoded images under `agent_outputs/`. Its supporting files are `IT_Policy.txt` and the system-performance datasets. It is separate from the Trail Guide GenAIOps workflow described above.

## Useful references

- [Infrastructure setup](docs/01-infrastructure-setup.md)
- [Prompt management](docs/02-prompt-management.md)
- [Prompt design and optimization](docs/03-design-optimize-prompts.md)
- [Automated evaluation](docs/04-automated-evaluation.md)
- [Monitoring and tracing](docs/05-monitoring-tracing.md)
