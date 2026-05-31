![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![OpenRouter](https://img.shields.io/badge/API-OpenRouter-6366f1)
![Model](https://img.shields.io/badge/model-claude--haiku--4.5-d97757)
![uv](https://img.shields.io/badge/package%20manager-uv-purple)

# Claude Code (my implementation)

My first agent built on top of an LLM API. It's a from-scratch implementation of a coding assistant in the style of Claude Code: it takes a natural language prompt, decides what to do via tool calls, and executes real actions on the filesystem and shell.

## How it works

The agent runs an **agent loop**: it sends the conversation to the model, and if the model responds with `tool_calls`, the agent executes each tool, appends the results to the message history, and loops again. When the model responds with plain text (no tool calls), the loop terminates and the response is printed.

Requests are sent to **OpenRouter** using the **OpenAI Python SDK** (OpenAI-compatible interface), targeting `anthropic/claude-haiku-4.5` as the underlying model.

## Implemented tools

The agent exposes the following tools to the model via OpenAI-compatible function calling:

- `read` — reads and returns the contents of a file.
- `write` — writes content to a file (creates or overwrites).
- `bash` — executes a shell command and returns its stdout (or stderr on failure).
- `edit` — replaces an exact string in a file with a new string.
- `grep` — searches file contents for a regex pattern, returning matches as `path:line:text`.
- `glob` — finds files matching a glob pattern (e.g. `**/*.py`).
- `ls` — lists the contents of a directory.
- `delete` — deletes a file.
- `mkdir` — creates a directory (including parent directories).

Each tool is declared with a JSON Schema and routed through a `TOOL_MAPPING` dictionary to the actual Python implementation.

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