[![progress-banner](https://backend.codecrafters.io/progress/claude-code/b4abc650-c2be-4bf8-a2fb-e873a916f892)](https://app.codecrafters.io/users/codecrafters-bot?r=2qF)

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![OpenRouter](https://img.shields.io/badge/API-OpenRouter-6366f1)
![Model](https://img.shields.io/badge/model-claude--haiku--4.5-d97757)
![uv](https://img.shields.io/badge/package%20manager-uv-purple)

# Claude Code (my implementation)

My first agent built on top of an LLM API. It's a from-scratch implementation of a coding assistant in the style of Claude Code: it takes a natural language prompt, decides what to do via tool calls, and executes real actions on the filesystem and shell.

Built as part of the [Build Your Own Claude Code](https://codecrafters.io/challenges/claude-code) challenge from CodeCrafters.

## How it works

The agent runs an **agent loop**: it sends the conversation to the model, and if the model responds with `tool_calls`, the agent executes each tool, appends the results to the message history, and loops again. When the model responds with plain text (no tool calls), the loop terminates and the response is printed.

Requests are sent to **OpenRouter** using the **OpenAI Python SDK** (OpenAI-compatible interface), targeting `anthropic/claude-haiku-4.5` as the underlying model.

## Implemented tools

The agent exposes three tools to the model via OpenAI-compatible function calling:

- `read` — reads and returns the contents of a file.
- `write` — writes content to a file (creates or overwrites).
- `bash` — executes a shell command and returns its stdout (or stderr on failure).

Each tool is declared with a JSON Schema and routed through a `TOOL_MAPPING` dictionary to the actual Python implementation.

## What I learned along the way

- **Agent loop mechanics**: structuring the `prompt → model response → tool execution → tool result → next turn` cycle, and knowing when to break out (no `tool_calls` in the response).
- **OpenAI-compatible tool calling**: defining `tools` with JSON Schema, parsing `tool_calls` from the response, and appending `role: "tool"` messages with the matching `tool_call_id` so the model can read the results on the next turn.
- **Stateless model, stateful conversation**: the API has no memory between calls, so the full message history (including assistant tool-call messages and tool result messages) must be sent on every request.
- **Using OpenRouter as a proxy**: pointing the OpenAI SDK at `https://openrouter.ai/api/v1` and selecting `anthropic/claude-haiku-4.5` instead of an OpenAI model, with no other client changes.
- **HTTP REST APIs**: working with auth headers, request/response shapes, and how `tool_calls` and tool result messages are structured.

## Stack

- Python 3.11+
- [OpenAI Python SDK](https://github.com/openai/openai-python) (used against OpenRouter)
- [OpenRouter](https://openrouter.ai/) → `anthropic/claude-haiku-4.5`
- `uv` for package and environment management

## Setup

Requires `uv` installed locally.

Set your OpenRouter API key:

```sh
export OPENROUTER_API_KEY="sk-or-..."
# optional: override the default base URL
export OPENROUTER_BASE_URL="https://openrouter.ai/api/v1"
```

## Usage

The entry point is `app/main.py`. Run via the provided script:

```sh
./your_program.sh -p "your prompt here"
```

You can optionally pass a filename as a positional argument, which gets added as a second user message:

```sh
./your_program.sh -p "explain what this file does" app/main.py
```

## CodeCrafters submission

```sh
codecrafters submit
```